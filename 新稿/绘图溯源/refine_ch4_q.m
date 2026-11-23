function refine_ch4_q()
% 加密过程噪声扫描；沿用选参种子，不使用性能评价种子。
here=fileparts(mfilename('fullpath'));
addpath(here);
for q=[1,3,4,5,6,8,10,12,16,30]
    label=sprintf('train_resample_q%d',q);
    diagnose_ch4_filtering(label,20,42000,q,.05,.2,{'adsb'},.6,true);
end
end
