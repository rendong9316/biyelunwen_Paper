function varargout=ukf_dispatch(action,ukf,varargin)
% 仅供隔离实验；不带标记的模板仍路由到原工程实现。
if isfield(ukf,'ch4_resampled') && ukf.ch4_resampled
    if isfield(ukf,'ukf_cv'),fh=@ukf_imm_ch4;else,fh=@ukf_jichu_ch4;end
elseif isfield(ukf,'ukf_cv') && isstruct(ukf.ukf_cv)
    fh=@ukf_imm;
elseif isfield(ukf,'maneuver_active') || (isfield(ukf,'filter_type') && strcmp(ukf.filter_type,'zishiying'))
    fh=@ukf_zishiying;
else
    fh=@ukf_jichu;
end
[varargout{1:nargout}]=fh(action,ukf,varargin{:});
end
