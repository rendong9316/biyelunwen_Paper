function diagnose_ch4_filtering(label,nseed,seedbase,q_psd,slow,fast,scenes,pds,resample)
% 现有滤波与航迹管理的独立对照；只读研究源码，不进入配准/站间融合。
assert(nargin>=8,'需要明确实验标签、种子、候选参数及场景');
if nargin<9,resample=false;end
here=fileparts(mfilename('fullpath'));
project=fileparts(fileparts(fileparts(here)));
root=fullfile(project,'文稿撰写','single_target_with-turn');
for d={'config','simulation','utils','ukf','tracker'}
    addpath(fullfile(root,d{1}));
end
prototype=fullfile(here,'实验实现','第四章');
if resample,addpath(prototype,'-begin');end
out=fullfile(here,'数据','第四章','诊断',label); if ~isfolder(out), mkdir(out); end
p=params_coverage_online();
% 隔离残余配准误差：所有通道使用同一固定虚高 300 km。
p.ionosphere_true_h_km=300; p.ionosphere_assumed_h_km=300;
p.radar1_assumed_h_km=300; p.radar2_assumed_h_km=300;
p.oracle_truth_terminate_enable=false;
p.imm_ct_omega_slow_deg=slow; p.imm_ct_omega_fast_deg=fast;
p.ukf_process_accel_psd_m2_s3=q_psd;
pr=radar_params(p,1);
methods={'CV_UKF','IMM_UKF'};

rec=struct([]); details=table();
for sceneidx=1:numel(scenes)
    scene=scenes{sceneidx};
    truth=reference(scene,here);
    n=height(truth);
    % 所有样本必须位于既定R1覆盖内，不能把出视场当作随机漏检。
    for k=1:n
        assert(radar_coverage_check(p.radar1_lon,p.radar1_lat,truth.lon(k),truth.lat(k), ...
            p.radar1_beam_center_deg,p),'参考轨迹不在视场内: %s/%d',scene,k);
    end
    if nseed>2, writetable(truth,fullfile(out,[scene '_reference.csv'])); end
    for pd=pds
        for seed=1:nseed
            rng(seedbase+seed,'twister');
            Z=zeros(n,3); raw=nan(n,2);
            % 先生成完整噪声序列，再抽漏检；两种检测概率具有嵌套命中。
            noise=randn(n,3); hitdraw=rand(n,1); hit=hitdraw<pd;
            det=cell(n,1);
            for k=1:n
                x=[truth.lon(k);truth.lon_rate(k);truth.lat(k);truth.lat_rate(k)];
                q=ukf_jichu('create',pr,p.radar1_lon,p.radar1_lat,p.radar1_tx_lon,p.radar1_tx_lat,30);
                Z(k,:)=ukf_jichu('measurement',q,x)'+noise(k,:).* ...
                    [pr.ukf_range_std_m,pr.ukf_azimuth_std_deg,pr.ukf_rv_std_ms];
                if hit(k)
                    [~,la,lo]=bistatic_inverse_solver(Z(k,1),Z(k,2), ...
                        p.radar1_tx_lon,p.radar1_tx_lat,p.radar1_lon,p.radar1_lat,300000);
                    raw(k,:)=[lo la];
                    det{k}=struct('prange',Z(k,1),'paz',Z(k,2),'pvr',Z(k,3), ...
                        'range_meas',Z(k,1),'azimuth_meas',Z(k,2),'radial_vel_meas',Z(k,3), ...
                        'drange',Z(k,1),'daz',Z(k,2),'lat',la,'lon',lo, ...
                        'frameID',k,'time_sec',truth.elapsed_sec(k),'aircraft_id',int32(1),'is_clutter',false);
                else
                    det{k}=[];
                end
            end
            result=cell(1,2); tracks_count=zeros(1,2);
            for m=1:2
                if resample
                    if m==1,fh=@ukf_jichu_ch4;else,fh=@ukf_imm_ch4;end
                else
                    if m==1, fh=@ukf_jichu; else, fh=@ukf_imm; end
                end
                tpl=fh('create',pr,p.radar1_lon,p.radar1_lat,p.radar1_tx_lon,p.radar1_tx_lat,30);
                identity_catalog={[truth.lon,truth.lat,truth.lon_rate,truth.lat_rate,truth.elapsed_sec]};
                % 身份目录供Oracle起始器分配目标槽位；不提供真值初值且关闭真值终止。
                [tracks,~,snap]=run_oracle_tracker_sequence(det,tpl,pr,identity_catalog,truth.elapsed_sec,false);
                tracks_count(m)=numel(tracks);
                result{m}=extract(snap,truth,hit);
            end
            % 两方法使用同一生命周期和点迹身份，按共同输出帧比较。
            common=isfinite(result{1}.lon)&isfinite(result{2}.lon);
            same=common&hit;
            rawerr=nan(n,1);
            for k=find(hit)'
                rawerr(k)=sphere_utils_haversine_distance(truth.lon(k),truth.lat(k),raw(k,1),raw(k,2))/1000;
            end
            for m=1:2
                r=result{m};
                row=struct('scene',scene,'pd',pd,'seed',seedbase+seed,'method',methods{m}, ...
                    'n_frames',n,'n_hits',sum(hit),'n_output',sum(isfinite(r.lon)), ...
                    'n_common',sum(common),'n_same_hit',sum(same),'n_tracks',tracks_count(m), ...
                    'raw_rmse_common_km',rmsfinite(rawerr(same)), ...
                    'position_rmse_hit_km',rmsfinite(r.pos_error_km(same)), ...
                    'position_rmse_all_km',rmsfinite(r.pos_error_km(common)), ...
                    'velocity_vector_rmse_ms',rmsfinite(r.velocity_error_ms(common)), ...
                    'nis_mean',mean(r.nis,'omitnan'),'nees_mean',mean(r.nees,'omitnan'), ...
                    'nis_coverage95',coverage(r.nis,.2158,9.3484), ...
                    'position_ellipse95',coverage(r.position_nees,0,5.991464547), ...
                    'nees_coverage95',coverage(r.nees,.4844,11.1433), ...
                    'output_fraction',mean(isfinite(r.lon)),'failed',~any(isfinite(r.lon)));
                rec=[rec;row]; %#ok<AGROW>
                if seed==1 && pd==.6 && nseed>2
                    r.elapsed_sec=truth.elapsed_sec;r.reference_lon=truth.lon;r.reference_lat=truth.lat;
                    r.raw_lon=raw(:,1);r.raw_lat=raw(:,2);r.raw_error_km=rawerr;
                    r.hit=hit;r.turn=truth.turn;
                    writetable(r,fullfile(out,[scene '_' methods{m} '_demo.csv']));
                end
            end
        end
        fprintf('CH4 %s Pd=%.1f seeds=%d finished\n',scene,pd,nseed);
    end
end
T=struct2table(rec);
name='monte_carlo.csv';
writetable(T,fullfile(out,name));
disp(groupsummary(T,{'scene','pd','method'},'mean', ...
    {'position_rmse_hit_km','position_rmse_all_km','velocity_vector_rmse_ms','nees_mean','output_fraction'}));
save(fullfile(out,'configuration.mat'),'label','nseed','seedbase','q_psd','slow','fast','scenes','pds','resample');
fprintf('MATLAB %s; results %s\n',version,out);
if resample,rmpath(prototype);end
end

function truth=reference(scene,here)
if startsWith(scene,'adsb')
    if strcmp(scene,'adsb')
        truth=readtable(fullfile(here,'数据','第三章','turn_reference.csv'));
    else
        truth=readtable(fullfile(here,'数据','第四章','诊断','validation_reference.csv'));
    end
    t=truth.elapsed_sec;lon=truth.lon;lat=truth.lat;
    % 参考速度仅用于量测生成和事后评估，绝不写入初始化。
    lr=gradient(lon,t); ar=gradient(lat,t);
    heading=unwrap(atan2(lr.*cosd(lat),ar));
    turn=abs(rad2deg(gradient(heading,t)))>.03;
else
    % 1秒球面积分，采样间隔30秒；相同纯仿真初始条件。
    tt=(0:1800)';lo=zeros(size(tt));la=lo;lo(1)=110;la(1)=30.1;
    heading=zeros(size(tt));turnfine=tt>=600 & tt<1200 & strcmp(scene,'turn');
    for j=2:numel(tt)
        heading(j)=heading(j-1)-.15*double(turnfine(j-1));
        [lo(j),la(j)]=sphere_utils_destination_point(lo(j-1),la(j-1),230,heading(j));
    end
    ix=1:30:numel(tt);t=tt(ix);lon=lo(ix);lat=la(ix);
    % 使用同一时刻的已知速度；方位从北顺时针。
    hd=heading(ix);lr=rad2deg(230*sind(hd)./(6371000*cosd(lat)));
    ar=rad2deg(230*cosd(hd)/6371000);turn=turnfine(ix);
end
truth=table(t,lon,lat,lr,ar,turn,'VariableNames', ...
    {'elapsed_sec','lon','lat','lon_rate','lat_rate','turn'});
end

function r=extract(snap,truth,hit)
n=height(truth);lon=nan(n,1);lat=lon;pos=lon;vel=lon;nis=lon;nees=lon;posnees=lon;id=lon;update=false(n,1);
for k=1:n
    if isempty(snap{k}.trackList), continue; end
    assert(numel(snap{k}.trackList)==1,'单目标出现重复活跃航迹');
    tr=snap{k}.trackList{1};x=tr.ukf.x;P=tr.ukf.P;
    lon(k)=x(1);lat(k)=x(3);id(k)=tr.id;update(k)=tr.updated;
    pos(k)=sphere_utils_haversine_distance(x(1),x(3),truth.lon(k),truth.lat(k))/1000;
    scale=6371000*pi/180;
    ev=scale*[x(2)*cosd(x(3))-truth.lon_rate(k)*cosd(truth.lat(k));x(4)-truth.lat_rate(k)];
    vel(k)=norm(ev);
    err=x-[truth.lon(k);truth.lon_rate(k);truth.lat(k);truth.lat_rate(k)];
    err(1)=mod(err(1)+180,360)-180;
    if rcond(P)>1e-16, nees(k)=err'*(P\err); end
    pp=P([1,3],[1,3]);if rcond(pp)>1e-16,posnees(k)=err([1,3])'*(pp\err([1,3]));end
    if tr.updated, nis(k)=tr.combined_nis; end
end
r=table(lon,lat,pos,vel,nis,nees,id,update,posnees, ...
    'VariableNames',{'lon','lat','pos_error_km','velocity_error_ms','nis','nees','track_id','updated','position_nees'});
end

function y=rmsfinite(x)
x=x(isfinite(x));if isempty(x), y=NaN; else, y=sqrt(mean(x.^2));end
end
function y=coverage(x,lo,hi)
x=x(isfinite(x));if isempty(x),y=NaN;else,y=mean(x>=lo & x<=hi);end
end
