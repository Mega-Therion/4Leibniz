// Lean compiler output
// Module: Leibniz.LexContinuitatis
// Imports: public import Init public meta import Init
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_LexContinuitatis_chi__floor__scaled;
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_LexContinuitatis_chi__mid__scaled;
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_LexContinuitatis_chi__ceil__scaled;
static lean_object* _init_lp_Leibniz_Leibniz_LexContinuitatis_chi__floor__scaled(void){
_start:
{
lean_object* v___x_1_; 
v___x_1_ = lean_unsigned_to_nat(7071u);
return v___x_1_;
}
}
static lean_object* _init_lp_Leibniz_Leibniz_LexContinuitatis_chi__mid__scaled(void){
_start:
{
lean_object* v___x_2_; 
v___x_2_ = lean_unsigned_to_nat(6931u);
return v___x_2_;
}
}
static lean_object* _init_lp_Leibniz_Leibniz_LexContinuitatis_chi__ceil__scaled(void){
_start:
{
lean_object* v___x_3_; 
v___x_3_ = lean_unsigned_to_nat(9539u);
return v___x_3_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_Leibniz_Leibniz_LexContinuitatis(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
lp_Leibniz_Leibniz_LexContinuitatis_chi__floor__scaled = _init_lp_Leibniz_Leibniz_LexContinuitatis_chi__floor__scaled();
lean_mark_persistent(lp_Leibniz_Leibniz_LexContinuitatis_chi__floor__scaled);
lp_Leibniz_Leibniz_LexContinuitatis_chi__mid__scaled = _init_lp_Leibniz_Leibniz_LexContinuitatis_chi__mid__scaled();
lean_mark_persistent(lp_Leibniz_Leibniz_LexContinuitatis_chi__mid__scaled);
lp_Leibniz_Leibniz_LexContinuitatis_chi__ceil__scaled = _init_lp_Leibniz_Leibniz_LexContinuitatis_chi__ceil__scaled();
lean_mark_persistent(lp_Leibniz_Leibniz_LexContinuitatis_chi__ceil__scaled);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
