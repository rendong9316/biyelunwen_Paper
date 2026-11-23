function evaluate_ch4_selected()
% 仅按已冻结的参数与评价种子运行；不在评价阶段调参。
here=fileparts(mfilename('fullpath'));
addpath(here);
selection=jsondecode(fileread(fullfile(here,'数据','第四章','诊断','parameter_selection.json')));
seeds=selection.evaluation_seeds;
assert(isequal(seeds(:)',[44001,44050]),'必须使用新的性能评价种子');
diagnose_ch4_filtering(selection.evaluation_folder,seeds(2)-seeds(1)+1,seeds(1)-1, ...
    selection.q,selection.slow,selection.fast, ...
    {'straight','turn','adsb','adsb_holdout'},[.6,.9],selection.resample);
end
