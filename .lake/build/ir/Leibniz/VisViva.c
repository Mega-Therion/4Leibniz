// Lean compiler output
// Module: Leibniz.VisViva
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
lean_object* lean_nat_mul(lean_object*, lean_object*);
lean_object* lean_nat_div(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_VisViva_vis__viva(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_VisViva_vis__viva___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_VisViva_acceleratio__limitis(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_VisViva_acceleratio__limitis___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_VisViva_vis__viva(lean_object* v_massa_1_, lean_object* v_velocitas_2_){
_start:
{
lean_object* v___x_3_; lean_object* v___x_4_; 
v___x_3_ = lean_nat_mul(v_massa_1_, v_velocitas_2_);
v___x_4_ = lean_nat_mul(v___x_3_, v_velocitas_2_);
lean_dec(v___x_3_);
return v___x_4_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_VisViva_vis__viva___boxed(lean_object* v_massa_5_, lean_object* v_velocitas_6_){
_start:
{
lean_object* v_res_7_; 
v_res_7_ = lp_Leibniz_Leibniz_VisViva_vis__viva(v_massa_5_, v_velocitas_6_);
lean_dec(v_velocitas_6_);
lean_dec(v_massa_5_);
return v_res_7_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_VisViva_acceleratio__limitis(lean_object* v_c_8_, lean_object* v_H__zero_9_){
_start:
{
lean_object* v___x_10_; lean_object* v___x_11_; lean_object* v___x_12_; 
v___x_10_ = lean_nat_mul(v_c_8_, v_H__zero_9_);
v___x_11_ = lean_unsigned_to_nat(6u);
v___x_12_ = lean_nat_div(v___x_10_, v___x_11_);
lean_dec(v___x_10_);
return v___x_12_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_VisViva_acceleratio__limitis___boxed(lean_object* v_c_13_, lean_object* v_H__zero_14_){
_start:
{
lean_object* v_res_15_; 
v_res_15_ = lp_Leibniz_Leibniz_VisViva_acceleratio__limitis(v_c_13_, v_H__zero_14_);
lean_dec(v_H__zero_14_);
lean_dec(v_c_13_);
return v_res_15_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_Leibniz_Leibniz_VisViva(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
