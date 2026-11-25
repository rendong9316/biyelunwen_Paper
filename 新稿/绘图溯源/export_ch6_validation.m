function export_ch6_validation(mode,seeds)
% 使用R2023a、第四章冻结q=6和完整预测协方差重采样；研究仓库只读。
if nargin<1,mode='smoke';end
if nargin<2,seeds=46001;end
here=fileparts(mfilename('fullpath'));
project=fileparts(fileparts(fileparts(here)));
root=fullfile(project,'文稿撰写','single_target_with-turn');
for d={'config','simulation','utils','ukf','tracker','fusion','evaluation','io','visualization'}
    addpath(fullfile(root,d{1}));
end
addpath(fullfile(here,'实验实现','第六章'),'-begin');
out=fullfile(here,'数据','第六章','冻结验证');
if ~isfolder(out),mkdir(out);end
cases={ 'vertical',[107.4 27 0;107.4 35 0]; ...
    'diag45',[105.6 28 0;109.4 32 0]; ...
    'near',[106 27 0;106 35 0]; 'far',[108.6 27 0;108.6 35 0]};
if strcmp(mode,'smoke'),cases=cases(1,:);end
for seed=seeds
    if ismember(mode,{'coverage','smoke'})
        for ci=1:size(cases,1)
            name=cases{ci,1}; p=params_coverage_online();
            p.aircraft_waypoints=cases{ci,2};p.aircraft_speed_ms=230;
            p=freeze(p,seed);
            execute('single_straight',name,p,out);
        end
    elseif strcmp(mode,'system')
        p=freeze(params_coverage_registered(),seed);
        execute('adsb_ns_all','system',p,out);
    elseif strcmp(mode,'model')
        for cfg={'wide','cruise'}
            p=freeze(simulation_params_oracle(),seed);
            % 模型集敏感性：只改变CT转弯率，其余参数及检测随机流相同。
            if strcmp(cfg{1},'wide')
                p.imm_ct_omega_slow_deg=.7;p.imm_ct_omega_fast_deg=1.5;
            end
            execute('adsb_0002',cfg{1},p,out);
        end
    else,error('未知mode');end
end
end

function p=freeze(p,seed)
p.random_seed=seed;p.dt_sec=30;
p.ukf_process_accel_psd_m2_s3=6;
p.imm_ct_omega_slow_deg=.05;p.imm_ct_omega_fast_deg=.2;
p.online_assoc_method='dualgate';p.online_fusion_method='SCC';
p.online_M=6;p.online_N=8;
p.online_fusion_methods={'SCC'};
p.oracle_truth_terminate_enable=false;
end

function execute(scene,label,p,out)
stem=sprintf('%s_%d',label,p.random_seed);
dest=fullfile(out,[stem '_samples.csv']);
configfile=fullfile(out,[stem '_configuration.json']);
if isfile(dest)&&isfile(configfile)
    old=jsondecode(fileread(configfile));
    if isfield(old,'extraction_version')&&old.extraction_version==4
        fprintf('已有完整导出 %s\n',stem);return;
    end
end
tic;
log=evalc("r=run_ch6_pipeline(scene,p,struct('verbose',false));");
assert(r.params.ukf_process_accel_psd_m2_s3==6);
assert(contains(which('ukf_imm'),'第六章'));
samples=table();lengths=table();
for tid=1:numel(r.truth_all)
    tr=r.truth_all{tid};n=r.n_frames;t=r.t1_grid(:);
    lon=interp1(tr(:,5),tr(:,1),t,'linear',NaN);
    lat=interp1(tr(:,5),tr(:,2),t,'linear',NaN);
    g1=false(n,1);g2=g1;id1=nan(n,1);id2=id1;cid=id1;ns=zeros(n,1);
    a1=nan(n,2);a2=a1;af=a1;ne1=nan(n,1);ne2=ne1;
    for k=find(isfinite(lon))'
        g1(k)=radar_coverage_check(p.radar1_lon,p.radar1_lat,lon(k),lat(k),p.radar1_beam_center_deg,p);
        g2(k)=radar_coverage_check(p.radar2_lon,p.radar2_lat,lon(k),lat(k),p.radar2_beam_center_deg,p);
        l1=local(r.trackSnapshots_R1{k},tid);l2=local(r.aligned_R2{k},tid);
        if ~isempty(l1),id1(k)=l1.id;a1(k,:)=position(l1);ne1(k)=nees(l1,lon(k),lat(k));end
        if ~isempty(l2),id2(k)=l2.id;a2(k,:)=position(l2);ne2(k)=nees(l2,lon(k),lat(k));end
        ct=r.ctSnap{k};
        for j=1:numel(ct)
            if ct(j).truth_idx~=tid || ct(j).n_src<1,continue;end
            % 对双源帧，须核验两条局部航迹确实属于同一参考目标。
            if ct(j).n_src==2
                u=l1;v=l2;
                if isempty(u)||u.id~=ct(j).src1_id,u=byid(r.trackSnapshots_R1{k},ct(j).src1_id);end
                if isempty(v)||v.id~=ct(j).src2_id,v=byid(r.aligned_R2{k},ct(j).src2_id);end
                if isempty(u)||isempty(v)||u.truth_idx~=tid||v.truth_idx~=tid,continue;end
            else
                u=l1;v=l2;
                if isempty(u)||u.id~=ct(j).src1_id,u=byid(r.trackSnapshots_R1{k},ct(j).src1_id);end
                if isempty(v)||v.id~=ct(j).src2_id,v=byid(r.aligned_R2{k},ct(j).src2_id);end
                if ~isempty(u)&&(u.truth_idx~=tid||ismember(u.type,[6 7])),u=[];end
                if ~isempty(v)&&(v.truth_idx~=tid||ismember(v.type,[6 7])),v=[];end
                if isempty(u)&&isempty(v),continue;end
            end
            if ct(j).n_src>ns(k)
                cid(k)=ct(j).id;ns(k)=ct(j).n_src;af(k,:)=[ct(j).x(1),ct(j).x(3)];
                if ~isempty(u),id1(k)=u.id;a1(k,:)=position(u);ne1(k)=nees(u,lon(k),lat(k));end
                if ~isempty(v),id2(k)=v.id;a2(k,:)=position(v);ne2(k)=nees(v,lon(k),lat(k));end
            end
        end
    end
    inside=g1|g2;
    % 几何实现度只计共同评价窗内、视场并集内的正确系统输出，预测尾迹不越界计数。
    geo1=sum(g1);geo2=sum(g2);uni=sum(inside);ov=sum(g1&g2);
    longest=longest_id(cid,inside);
    base1=longest_id(id1,inside);base2=longest_id(id2,inside);
    row=table(tid,geo1,geo2,uni,ov,longest,base1,base2, ...
        longest/max(1,max(base1,base2)),longest/max(1,uni), ...
        'VariableNames',{'target','geometry_r1','geometry_r2','geometry_union','geometry_overlap', ...
        'system_longest','local_r1_longest','local_r2_longest','track_ratio','union_realization'});
    lengths=[lengths;row]; %#ok<AGROW>
    valid=isfinite(lon);
    part=table(repmat(tid,sum(valid),1),find(valid),t(valid),lon(valid),lat(valid), ...
        g1(valid),g2(valid),id1(valid),id2(valid),cid(valid),ns(valid), ...
        a1(valid,1),a1(valid,2),a2(valid,1),a2(valid,2),af(valid,1),af(valid,2),ne1(valid),ne2(valid), ...
        'VariableNames',{'target','frame','time_sec','truth_lon','truth_lat','geometry_r1','geometry_r2', ...
        'local1_id','local2_id','system_id','n_sources','r1_lon','r1_lat','r2_lon','r2_lat', ...
        'system_lon','system_lat','nees1','nees2'});
    samples=[samples;part]; %#ok<AGROW>
end
writetable(lengths,fullfile(out,[stem '_lengths.csv']));
fid=fopen(fullfile(out,[stem '_log.txt']),'w','n','UTF-8');fprintf(fid,'%s',log);fclose(fid);
meta=struct('matlab',version,'scene',scene,'seed',p.random_seed,'q',6, ...
    'slow',p.imm_ct_omega_slow_deg,'fast',p.imm_ct_omega_fast_deg, ...
    'filter','第四章完整预测协方差重采样','causal',true,'extraction_version',4,'params',p);
fid=fopen(fullfile(out,[stem '_configuration.json']),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(meta));fclose(fid);
writetable(samples,dest);
fprintf('CH6 %s %s frames=%d targets=%d %.1fs\n',label,stem,r.n_frames,numel(r.truth_all),toc);
end

function s=local(snap,tid)
s=[];if isempty(snap)||~isfield(snap,'trackList'),return;end
for j=1:numel(snap.trackList)
    u=snap.trackList{j};
    if isfield(u,'truth_idx')&&u.truth_idx==tid&&isfield(u,'type')&&~ismember(u.type,[6 7])
        if isempty(s)||u.id<s.id,s=u;end
    end
end
end
function s=byid(snap,id)
s=[];if isempty(snap)||~isfield(snap,'trackList'),return;end
for j=1:numel(snap.trackList)
    if snap.trackList{j}.id==id,s=snap.trackList{j};return;end
end
end
function a=position(s),a=[s.ukf.x(1) s.ukf.x(3)];end
function v=nees(s,lo,la)
scale=diag([111.32*cosd(la),110.57]);
e=scale*(position(s)-[lo la])';P=scale*s.ukf.P([1 3],[1 3])*scale';
v=e'*(P\e);
end
function n=longest_id(ids,mask)
n=0;u=unique(ids(mask&isfinite(ids)));
for id=u',n=max(n,sum(mask&ids==id));end
end
