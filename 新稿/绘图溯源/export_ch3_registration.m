function export_ch3_registration()
% 在 R2023a 中调用现有标定、正演与双基地反演函数；不修改研究工程。
here = fileparts(mfilename('fullpath'));
project = fileparts(fileparts(fileparts(here)));
root = fullfile(project, '文稿撰写', 'single_target_with-turn');
for d = {'config','simulation','utils'}
    addpath(fullfile(root,d{1}));
end
out = fullfile(here, '数据', '第三章');
assert(isfolder(out), '请先运行 prepare_ch3_turn.py');
p = params_coverage_registered();
p.adsb_csv_path = fullfile(root, p.adsb_csv_path);
p.calib_cache_enable = false;
seeds = 42:51;
records = zeros(numel(seeds)*2, 12);
for j = 1:numel(seeds)
    p.random_seed = seeds(j);
    [~,~,~,~,reg] = calibrate_radar_bias(p);
    assert(reg.converged1 && reg.converged2, '标定未收敛');
    for st = 1:2
        eta = reg.(sprintf('eta%d',st));
        bound = sqrt(diag(reg.(sprintf('crlb%d',st))))';
        records(2*j-2+st,:) = [seeds(j),st,reg.(sprintf('n%d',st)),eta(:)',bound, ...
                              320,20*(st==1)-15*(st==2),-3*(st==1)+3.5*(st==2)];
    end
    if j==1, demo_reg=reg; end
end
names = {'seed','station','n_obs','h_km','dR_km','dtheta_deg', ...
         'bound_h_km','bound_dR_km','bound_dtheta_deg','true_h_km','true_dR_km','true_dtheta_deg'};
writetable(array2table(records,'VariableNames',names),fullfile(out,'calibration_mc.csv'));

ref = readtable(fullfile(out,'turn_reference.csv'));
n = height(ref);
rng(20261123,'twister');
Rg = skywave_geometry('group_range',p.radar1_tx_lon,p.radar1_tx_lat, ...
    p.radar1_lon,p.radar1_lat,ref.lon,ref.lat,p.ionosphere_true_h_km*1000) ...
    +p.radar1_range_bias_m+randn(n,1)*p.radar1_range_noise_std_m;
az = skywave_geometry('azimuth',p.radar1_lon,p.radar1_lat,ref.lon,ref.lat) ...
    +p.radar1_azimuth_bias_deg+randn(n,1)*p.radar1_azimuth_noise_std_deg;
eta = demo_reg.eta1;
before = zeros(n,2); after = zeros(n,2);
for k=1:n
    [~,before(k,2),before(k,1)] = bistatic_inverse_solver(Rg(k),az(k), ...
        p.radar1_tx_lon,p.radar1_tx_lat,p.radar1_lon,p.radar1_lat,300000);
    [~,after(k,2),after(k,1)] = bistatic_inverse_solver(Rg(k)-eta(2)*1000,az(k)-eta(3), ...
        p.radar1_tx_lon,p.radar1_tx_lat,p.radar1_lon,p.radar1_lat,eta(1)*1000);
end
err0 = zeros(n,1); err1 = zeros(n,1);
for k=1:n
    err0(k)=sphere_utils_haversine_distance(ref.lon(k),ref.lat(k),before(k,1),before(k,2))/1000;
    err1(k)=sphere_utils_haversine_distance(ref.lon(k),ref.lat(k),after(k,1),after(k,2))/1000;
end
T=table(ref.elapsed_sec,ref.lon,ref.lat,Rg,az,before(:,1),before(:,2),after(:,1),after(:,2),err0,err1, ...
    'VariableNames',{'elapsed_sec','reference_lon','reference_lat','range_m','azimuth_deg', ...
    'before_lon','before_lat','after_lon','after_lat','before_error_km','after_error_km'});
assert(all(isfinite(T{:,:}),'all'),'演示结果存在无效值');
writetable(T,fullfile(out,'turn_registration.csv'));
fprintf('演示：N=%d，配准前RMSE=%.3fkm，配准后RMSE=%.3fkm\n',n,sqrt(mean(err0.^2)),sqrt(mean(err1.^2)));
fprintf('本次导出由 MATLAB %s 生成\n',version);
end
