function check_ch4_process_noise()
% 直接核对现有UKF返回的Sigma点二阶矩是否包含已添加的加性过程噪声。
here=fileparts(mfilename('fullpath'));
root=fullfile(fileparts(fileparts(fileparts(here))),'文稿撰写','single_target_with-turn');
for d={'config','simulation','utils','ukf'},addpath(fullfile(root,d{1}));end
addpath(fullfile(here,'实验实现','第四章'));
p=params_coverage_online();p.radar1_assumed_h_km=300;p.ukf_process_accel_psd_m2_s3=2;
p=radar_params(p,1);
ratios=zeros(1,2);
for j=1:2
    if j==1,fh=@ukf_jichu;else,fh=@ukf_jichu_ch4;end
    u=fh('create',p,92.5,31.45,88.5,31.45,30);
    u.x=[110;0;32;.002];u.initialized=true;
    metric=diag([6371000*pi/180*cosd(32),6371000*pi/180*cosd(32),6371000*pi/180,6371000*pi/180]);
    u.P=metric\diag([1e6,100,1e6,100])/metric';
    [x,P,X,~,~,~,u]=fh('prepare',u);
    C=zeros(4);
    for k=1:size(X,2),e=X(:,k)-x;C=C+u.Wc(k)*(e*e');end
    ratios(j)=norm(metric*(P-C)*metric','fro')/norm(metric*P*metric','fro');
end
fprintf('Sigma协方差相对缺口：原实现 %.8g，重采样实现 %.8g\n',ratios);
assert(ratios(1)>1e-3,'未复现过程噪声的二阶矩缺口');
assert(ratios(2)<1e-8,'重采样后Sigma点二阶矩仍与预测协方差不符');
out=fullfile(here,'数据','第四章','诊断','sigma_moments.csv');
writetable(table(["original";"resampled"],ratios','VariableNames',{'implementation','relative_covariance_gap'}),out);
end
