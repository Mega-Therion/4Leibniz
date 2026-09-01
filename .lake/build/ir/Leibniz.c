// Lean compiler output
// Module: Leibniz
// Imports: public import Init public meta import Init public import Leibniz.Characteristica public import Leibniz.SpatiumRelativum public import Leibniz.VisViva public import Leibniz.LexContinuitatis public import Leibniz.Harmonia public import Leibniz.Calculemus
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
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Leibniz_Leibniz_Characteristica(uint8_t builtin);
lean_object* initialize_Leibniz_Leibniz_SpatiumRelativum(uint8_t builtin);
lean_object* initialize_Leibniz_Leibniz_VisViva(uint8_t builtin);
lean_object* initialize_Leibniz_Leibniz_LexContinuitatis(uint8_t builtin);
lean_object* initialize_Leibniz_Leibniz_Harmonia(uint8_t builtin);
lean_object* initialize_Leibniz_Leibniz_Calculemus(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_Leibniz_Leibniz(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Leibniz_Leibniz_Characteristica(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Leibniz_Leibniz_SpatiumRelativum(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Leibniz_Leibniz_VisViva(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Leibniz_Leibniz_LexContinuitatis(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Leibniz_Leibniz_Harmonia(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Leibniz_Leibniz_Calculemus(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
