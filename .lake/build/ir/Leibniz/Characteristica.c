// Lean compiler output
// Module: Leibniz.Characteristica
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
lean_object* lean_nat_to_int(lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
lean_object* l_Repr_addAppParen(lean_object*, lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorIdx(uint8_t);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_toCtorIdx(uint8_t);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_toCtorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim(lean_object*, lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_Leibniz_Leibniz_Characteristica_Dyas_ofNat(lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ofNat___boxed(lean_object*);
LEAN_EXPORT uint8_t lp_Leibniz_Leibniz_Characteristica_instDecidableEqDyas(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_instDecidableEqDyas___boxed(lean_object*, lean_object*);
static const lean_string_object lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 35, .m_capacity = 35, .m_length = 34, .m_data = "Leibniz.Characteristica.Dyas.Nihil"};
static const lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__0 = (const lean_object*)&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__0_value;
static const lean_ctor_object lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__0_value)}};
static const lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__1 = (const lean_object*)&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__1_value;
static const lean_string_object lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 33, .m_capacity = 33, .m_length = 32, .m_data = "Leibniz.Characteristica.Dyas.Ens"};
static const lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__2 = (const lean_object*)&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__2_value;
static const lean_ctor_object lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__2_value)}};
static const lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__3 = (const lean_object*)&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__3_value;
static lean_once_cell_t lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__4;
static lean_once_cell_t lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__5;
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr(uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_Leibniz_Leibniz_Characteristica_instReprDyas___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas___closed__0 = (const lean_object*)&lp_Leibniz_Leibniz_Characteristica_instReprDyas___closed__0_value;
LEAN_EXPORT const lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas = (const lean_object*)&lp_Leibniz_Leibniz_Characteristica_instReprDyas___closed__0_value;
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_tensio(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_tensio___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorIdx(uint8_t v_x_1_){
_start:
{
if (v_x_1_ == 0)
{
lean_object* v___x_2_; 
v___x_2_ = lean_unsigned_to_nat(0u);
return v___x_2_;
}
else
{
lean_object* v___x_3_; 
v___x_3_ = lean_unsigned_to_nat(1u);
return v___x_3_;
}
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorIdx___boxed(lean_object* v_x_4_){
_start:
{
uint8_t v_x_boxed_5_; lean_object* v_res_6_; 
v_x_boxed_5_ = lean_unbox(v_x_4_);
v_res_6_ = lp_Leibniz_Leibniz_Characteristica_Dyas_ctorIdx(v_x_boxed_5_);
return v_res_6_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_toCtorIdx(uint8_t v_x_7_){
_start:
{
lean_object* v___x_8_; 
v___x_8_ = lp_Leibniz_Leibniz_Characteristica_Dyas_ctorIdx(v_x_7_);
return v___x_8_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_toCtorIdx___boxed(lean_object* v_x_9_){
_start:
{
uint8_t v_x_4__boxed_10_; lean_object* v_res_11_; 
v_x_4__boxed_10_ = lean_unbox(v_x_9_);
v_res_11_ = lp_Leibniz_Leibniz_Characteristica_Dyas_toCtorIdx(v_x_4__boxed_10_);
return v_res_11_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim___redArg(lean_object* v_k_12_){
_start:
{
lean_inc(v_k_12_);
return v_k_12_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim___redArg___boxed(lean_object* v_k_13_){
_start:
{
lean_object* v_res_14_; 
v_res_14_ = lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim___redArg(v_k_13_);
lean_dec(v_k_13_);
return v_res_14_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim(lean_object* v_motive_15_, lean_object* v_ctorIdx_16_, uint8_t v_t_17_, lean_object* v_h_18_, lean_object* v_k_19_){
_start:
{
lean_inc(v_k_19_);
return v_k_19_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim___boxed(lean_object* v_motive_20_, lean_object* v_ctorIdx_21_, lean_object* v_t_22_, lean_object* v_h_23_, lean_object* v_k_24_){
_start:
{
uint8_t v_t_boxed_25_; lean_object* v_res_26_; 
v_t_boxed_25_ = lean_unbox(v_t_22_);
v_res_26_ = lp_Leibniz_Leibniz_Characteristica_Dyas_ctorElim(v_motive_20_, v_ctorIdx_21_, v_t_boxed_25_, v_h_23_, v_k_24_);
lean_dec(v_k_24_);
lean_dec(v_ctorIdx_21_);
return v_res_26_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim___redArg(lean_object* v_Nihil_27_){
_start:
{
lean_inc(v_Nihil_27_);
return v_Nihil_27_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim___redArg___boxed(lean_object* v_Nihil_28_){
_start:
{
lean_object* v_res_29_; 
v_res_29_ = lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim___redArg(v_Nihil_28_);
lean_dec(v_Nihil_28_);
return v_res_29_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim(lean_object* v_motive_30_, uint8_t v_t_31_, lean_object* v_h_32_, lean_object* v_Nihil_33_){
_start:
{
lean_inc(v_Nihil_33_);
return v_Nihil_33_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim___boxed(lean_object* v_motive_34_, lean_object* v_t_35_, lean_object* v_h_36_, lean_object* v_Nihil_37_){
_start:
{
uint8_t v_t_boxed_38_; lean_object* v_res_39_; 
v_t_boxed_38_ = lean_unbox(v_t_35_);
v_res_39_ = lp_Leibniz_Leibniz_Characteristica_Dyas_Nihil_elim(v_motive_34_, v_t_boxed_38_, v_h_36_, v_Nihil_37_);
lean_dec(v_Nihil_37_);
return v_res_39_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim___redArg(lean_object* v_Ens_40_){
_start:
{
lean_inc(v_Ens_40_);
return v_Ens_40_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim___redArg___boxed(lean_object* v_Ens_41_){
_start:
{
lean_object* v_res_42_; 
v_res_42_ = lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim___redArg(v_Ens_41_);
lean_dec(v_Ens_41_);
return v_res_42_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim(lean_object* v_motive_43_, uint8_t v_t_44_, lean_object* v_h_45_, lean_object* v_Ens_46_){
_start:
{
lean_inc(v_Ens_46_);
return v_Ens_46_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim___boxed(lean_object* v_motive_47_, lean_object* v_t_48_, lean_object* v_h_49_, lean_object* v_Ens_50_){
_start:
{
uint8_t v_t_boxed_51_; lean_object* v_res_52_; 
v_t_boxed_51_ = lean_unbox(v_t_48_);
v_res_52_ = lp_Leibniz_Leibniz_Characteristica_Dyas_Ens_elim(v_motive_47_, v_t_boxed_51_, v_h_49_, v_Ens_50_);
lean_dec(v_Ens_50_);
return v_res_52_;
}
}
LEAN_EXPORT uint8_t lp_Leibniz_Leibniz_Characteristica_Dyas_ofNat(lean_object* v_n_53_){
_start:
{
lean_object* v___x_54_; uint8_t v___x_55_; 
v___x_54_ = lean_unsigned_to_nat(0u);
v___x_55_ = lean_nat_dec_le(v_n_53_, v___x_54_);
if (v___x_55_ == 0)
{
uint8_t v___x_56_; 
v___x_56_ = 1;
return v___x_56_;
}
else
{
uint8_t v___x_57_; 
v___x_57_ = 0;
return v___x_57_;
}
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_Dyas_ofNat___boxed(lean_object* v_n_58_){
_start:
{
uint8_t v_res_59_; lean_object* v_r_60_; 
v_res_59_ = lp_Leibniz_Leibniz_Characteristica_Dyas_ofNat(v_n_58_);
lean_dec(v_n_58_);
v_r_60_ = lean_box(v_res_59_);
return v_r_60_;
}
}
LEAN_EXPORT uint8_t lp_Leibniz_Leibniz_Characteristica_instDecidableEqDyas(uint8_t v_x_61_, uint8_t v_y_62_){
_start:
{
lean_object* v___x_63_; lean_object* v___x_64_; uint8_t v___x_65_; 
v___x_63_ = lp_Leibniz_Leibniz_Characteristica_Dyas_ctorIdx(v_x_61_);
v___x_64_ = lp_Leibniz_Leibniz_Characteristica_Dyas_ctorIdx(v_y_62_);
v___x_65_ = lean_nat_dec_eq(v___x_63_, v___x_64_);
lean_dec(v___x_64_);
lean_dec(v___x_63_);
return v___x_65_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_instDecidableEqDyas___boxed(lean_object* v_x_66_, lean_object* v_y_67_){
_start:
{
uint8_t v_x_13__boxed_68_; uint8_t v_y_14__boxed_69_; uint8_t v_res_70_; lean_object* v_r_71_; 
v_x_13__boxed_68_ = lean_unbox(v_x_66_);
v_y_14__boxed_69_ = lean_unbox(v_y_67_);
v_res_70_ = lp_Leibniz_Leibniz_Characteristica_instDecidableEqDyas(v_x_13__boxed_68_, v_y_14__boxed_69_);
v_r_71_ = lean_box(v_res_70_);
return v_r_71_;
}
}
static lean_object* _init_lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__4(void){
_start:
{
lean_object* v___x_78_; lean_object* v___x_79_; 
v___x_78_ = lean_unsigned_to_nat(2u);
v___x_79_ = lean_nat_to_int(v___x_78_);
return v___x_79_;
}
}
static lean_object* _init_lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__5(void){
_start:
{
lean_object* v___x_80_; lean_object* v___x_81_; 
v___x_80_ = lean_unsigned_to_nat(1u);
v___x_81_ = lean_nat_to_int(v___x_80_);
return v___x_81_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr(uint8_t v_x_82_, lean_object* v_prec_83_){
_start:
{
lean_object* v___y_85_; lean_object* v___y_92_; 
if (v_x_82_ == 0)
{
lean_object* v___x_98_; uint8_t v___x_99_; 
v___x_98_ = lean_unsigned_to_nat(1024u);
v___x_99_ = lean_nat_dec_le(v___x_98_, v_prec_83_);
if (v___x_99_ == 0)
{
lean_object* v___x_100_; 
v___x_100_ = lean_obj_once(&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__4, &lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__4_once, _init_lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__4);
v___y_85_ = v___x_100_;
goto v___jp_84_;
}
else
{
lean_object* v___x_101_; 
v___x_101_ = lean_obj_once(&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__5, &lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__5_once, _init_lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__5);
v___y_85_ = v___x_101_;
goto v___jp_84_;
}
}
else
{
lean_object* v___x_102_; uint8_t v___x_103_; 
v___x_102_ = lean_unsigned_to_nat(1024u);
v___x_103_ = lean_nat_dec_le(v___x_102_, v_prec_83_);
if (v___x_103_ == 0)
{
lean_object* v___x_104_; 
v___x_104_ = lean_obj_once(&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__4, &lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__4_once, _init_lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__4);
v___y_92_ = v___x_104_;
goto v___jp_91_;
}
else
{
lean_object* v___x_105_; 
v___x_105_ = lean_obj_once(&lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__5, &lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__5_once, _init_lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__5);
v___y_92_ = v___x_105_;
goto v___jp_91_;
}
}
v___jp_84_:
{
lean_object* v___x_86_; lean_object* v___x_87_; uint8_t v___x_88_; lean_object* v___x_89_; lean_object* v___x_90_; 
v___x_86_ = ((lean_object*)(lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__1));
lean_inc(v___y_85_);
v___x_87_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_87_, 0, v___y_85_);
lean_ctor_set(v___x_87_, 1, v___x_86_);
v___x_88_ = 0;
v___x_89_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_89_, 0, v___x_87_);
lean_ctor_set_uint8(v___x_89_, sizeof(void*)*1, v___x_88_);
v___x_90_ = l_Repr_addAppParen(v___x_89_, v_prec_83_);
return v___x_90_;
}
v___jp_91_:
{
lean_object* v___x_93_; lean_object* v___x_94_; uint8_t v___x_95_; lean_object* v___x_96_; lean_object* v___x_97_; 
v___x_93_ = ((lean_object*)(lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___closed__3));
lean_inc(v___y_92_);
v___x_94_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_94_, 0, v___y_92_);
lean_ctor_set(v___x_94_, 1, v___x_93_);
v___x_95_ = 0;
v___x_96_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_96_, 0, v___x_94_);
lean_ctor_set_uint8(v___x_96_, sizeof(void*)*1, v___x_95_);
v___x_97_ = l_Repr_addAppParen(v___x_96_, v_prec_83_);
return v___x_97_;
}
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr___boxed(lean_object* v_x_106_, lean_object* v_prec_107_){
_start:
{
uint8_t v_x_121__boxed_108_; lean_object* v_res_109_; 
v_x_121__boxed_108_ = lean_unbox(v_x_106_);
v_res_109_ = lp_Leibniz_Leibniz_Characteristica_instReprDyas_repr(v_x_121__boxed_108_, v_prec_107_);
lean_dec(v_prec_107_);
return v_res_109_;
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_tensio(uint8_t v_d_u2081_112_, uint8_t v_d_u2082_113_){
_start:
{
if (v_d_u2081_112_ == 0)
{
if (v_d_u2082_113_ == 1)
{
lean_object* v___x_114_; 
v___x_114_ = lean_unsigned_to_nat(1u);
return v___x_114_;
}
else
{
lean_object* v___x_115_; 
v___x_115_ = lean_unsigned_to_nat(0u);
return v___x_115_;
}
}
else
{
if (v_d_u2082_113_ == 0)
{
lean_object* v___x_116_; 
v___x_116_ = lean_unsigned_to_nat(1u);
return v___x_116_;
}
else
{
lean_object* v___x_117_; 
v___x_117_ = lean_unsigned_to_nat(0u);
return v___x_117_;
}
}
}
}
LEAN_EXPORT lean_object* lp_Leibniz_Leibniz_Characteristica_tensio___boxed(lean_object* v_d_u2081_118_, lean_object* v_d_u2082_119_){
_start:
{
uint8_t v_d_u2081_boxed_120_; uint8_t v_d_u2082_boxed_121_; lean_object* v_res_122_; 
v_d_u2081_boxed_120_ = lean_unbox(v_d_u2081_118_);
v_d_u2082_boxed_121_ = lean_unbox(v_d_u2082_119_);
v_res_122_ = lp_Leibniz_Leibniz_Characteristica_tensio(v_d_u2081_boxed_120_, v_d_u2082_boxed_121_);
return v_res_122_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_Leibniz_Leibniz_Characteristica(uint8_t builtin) {
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
