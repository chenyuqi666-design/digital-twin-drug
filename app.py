import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="数字孪生器官：AI虚拟试药", page_icon="🧬", layout="wide")

# ============ 页面标题 ============
st.title("🧬 数字孪生器官：AI能在虚拟人体里试药吗？")
st.markdown("""
在传统的药物研发中，往往需要经历漫长的动物实验和人体临床试验。而现在，借助**数字孪生技术（Digital Twins）**和人工智能，
科学家可以在超级计算机里构建一个与真实人体器官高度一致的"虚拟替身"。在这个虚拟器官上，
AI 可以模拟药物分子的进入、与靶点的结合以及引发的生理反应，从而提前筛选出有效药物并预测毒副作用。
""")
st.divider()

# ============ 侧边栏：参数输入 ============
with st.sidebar:
    st.header("⚙️ 仿真参数设置")
    
    st.subheader("💊 药物属性")
    drug = st.selectbox("选择候选药物分子",
        ["Drug-A (靶向药)", "Drug-B (化疗药)", "Drug-C (免疫调节剂)", "Drug-D (安慰剂对照)"])
    target_affinity = st.slider("靶点亲和力 Kd (nM)", 1, 100, 25,
        help="数值越小，药物与靶点结合越紧密")
    lipophilicity = st.slider("脂溶性 logP", -2.0, 5.0, 1.5, 0.1,
        help="影响药物穿透细胞膜的能力")
    
    st.subheader("📋 给药方案")
    dose = st.slider("给药剂量 (mg/kg)", 1, 200, 50)
    route = st.selectbox("给药途径", ["静脉注射", "口服", "皮下注射"])
    frequency = st.selectbox("给药频率", ["单次给药", "每日一次", "每12小时一次"])
    duration = st.slider("疗程天数", 1, 30, 7)
    
    st.subheader("🧑 虚拟患者特征")
    age = st.slider("患者年龄", 18, 90, 45)
    weight = st.slider("体重 (kg)", 40, 120, 70)
    organ_function = st.selectbox("肝肾功能状态", ["正常", "轻度损伤", "中度损伤", "重度损伤"])
    genotype = st.selectbox("代谢酶基因型", ["快代谢型", "正常代谢型", "慢代谢型"])
    
    st.divider()
    run = st.button("🚀 启动AI虚拟仿真", use_container_width=True)

# ============ 参数换算 ============
# 给药途径的生物利用度
bioavail_map = {"静脉注射": 1.0, "口服": 0.65, "皮下注射": 0.85}
bioavail = bioavail_map[route]

# 肝肾功能对清除率的影响
organ_factor = {"正常": 1.0, "轻度损伤": 0.75, "中度损伤": 0.5, "重度损伤": 0.3}
of = organ_factor[organ_function]

# 基因型对代谢的影响
geno_factor = {"快代谢型": 1.3, "正常代谢型": 1.0, "慢代谢型": 0.6}
gf = geno_factor[genotype]

# 年龄影响分布容积
age_factor = 1.0 - (age - 45) * 0.004 if age > 45 else 1.0

# 药物基础效价
drug_potency = {"Drug-A (靶向药)": 1.0, "Drug-B (化疗药)": 0.7,
                "Drug-C (免疫调节剂)": 0.85, "Drug-D (安慰剂对照)": 0.05}
potency = drug_potency[drug]

# 表观分布容积 (L)
Vd = weight * 0.6 * age_factor
# 消除速率常数
ke = 0.15 * of * gf
# 半衰期
t_half = np.log(2) / ke

# 有效浓度与中毒浓度阈值
C_eff = 5.0
C_tox = 40.0

# ============ 主区域 ============
st.header("🧪 虚拟试药模拟器 (In Silico Trial)")
st.caption("调整左侧参数，模拟不同药物在数字孪生心脏上的反应")

if run:
    with st.spinner("AI 正在虚拟器官上进行仿真计算..."):
        # ---------- 药代动力学曲线 ----------
        t = np.linspace(0, 24, 300)
        C0 = (dose * bioavail) / Vd
        
        if frequency == "单次给药":
            C = C0 * np.exp(-ke * t)
        elif frequency == "每日一次":
            C = np.zeros_like(t)
            for k in range(duration):
                C += np.where(t >= k*24, C0 * np.exp(-ke * (t - k*24)), 0)
        else:
            C = np.zeros_like(t)
            for k in range(duration*2):
                C += np.where(t >= k*12, C0 * np.exp(-ke * (t - k*12)), 0)
        
        # ---------- 效应曲线（Hill方程）----------
        IC50 = 20.0 / (potency * (100 / target_affinity) ** 0.5)
        effect = 100 / (1 + (IC50 / np.maximum(C, 0.01)) ** 1.8)
        
        # ---------- 群体模拟 ----------
        np.random.seed(42)
        n = 1000
        pop_weight = np.random.normal(weight, weight*0.15, n)
        pop_ke = np.random.normal(ke, ke*0.2, n)
        pop_Vd = np.random.normal(Vd, Vd*0.15, n)
        pop_Cmax = (dose * bioavail) / pop_Vd
        pop_effect = 100 / (1 + (IC50 / np.maximum(pop_Cmax, 0.01)) ** 1.8)
        
        eff_rate = np.mean(pop_effect > 50) * 100
        tox_rate = np.mean(pop_Cmax > C_tox) * 100

    # ---------- 指标卡片 ----------
    st.subheader("📊 仿真结果面板")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("峰值血药浓度", f"{C0:.2f} μg/mL")
    c2.metric("消除半衰期", f"{t_half:.1f} h")
    c3.metric("群体有效率", f"{eff_rate:.1f}%", delta=f"{eff_rate-50:.1f}% vs 基线")
    c4.metric("毒性风险率", f"{tox_rate:.1f}%", delta=f"-{100-tox_rate:.1f}%", delta_color="inverse")
    
    st.divider()
    
    # ---------- 标签页 ----------
    tab1, tab2, tab3, tab4 = st.tabs(["📈 药代动力学", "💊 剂量-效应关系", "⚠️ 安全性评估", "👥 群体模拟"])
    
    with tab1:
        st.markdown("**24小时血药浓度-时间曲线**")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=t, y=C, name="血药浓度",
                                  line=dict(color="#2E86AB", width=3)))
        fig1.add_hline(y=C_eff, line_dash="dash", line_color="green",
                       annotation_text="有效浓度阈值")
        fig1.add_hline(y=C_tox, line_dash="dash", line_color="red",
                       annotation_text="中毒阈值")
        fig1.update_layout(xaxis_title="时间 (h)", yaxis_title="浓度 (μg/mL)",
                          height=420, template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)
        
        above_eff = np.sum(C > C_eff) / len(C) * 100
        st.info(f"💡 该方案下，血药浓度有 **{above_eff:.1f}%** 的时间处于有效区间。"
                f"半衰期 **{t_half:.1f} 小时**，建议给药间隔 **{t_half*2:.0f} 小时**。")
    
    with tab2:
        st.markdown("**剂量-效应关系曲线（Hill方程）**")
        doses = np.linspace(1, 200, 200)
        effects = []
        for d in doses:
            c_max = (d * bioavail) / Vd
            effects.append(100 / (1 + (IC50 / max(c_max, 0.01)) ** 1.8))
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=doses, y=effects, name="效应",
                                  line=dict(color="#A23B72", width=3)))
        fig2.add_scatter(x=[dose], y=[100 / (1 + (IC50/max(C0,0.01))**1.8)],
                         mode="markers", marker=dict(size=14, color="red"),
                         name="当前剂量")
        fig2.update_layout(xaxis_title="剂量 (mg/kg)", yaxis_title="最大效应 (%)",
                           height=420, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(f"当前药物的 IC50 约为 **{IC50:.2f} μg/mL**，曲线呈典型 S 型，"
                   f"说明存在剂量依赖性效应。")
    
    with tab3:
        st.markdown("**多维安全性雷达评估**")
        cardio = min(100, C0 * 1.8 + (1-of)*40)
        hepato = min(100, dose * 0.35 + (1-of)*50)
        nephro = min(100, C0 * 1.2 + (1-of)*35)
        immuno = min(100, potency * 30 + lipophilicity * 8)
        efficacy = min(100, eff_rate)
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatterpolar(
            r=[efficacy, cardio, hepato, nephro, immuno],
            theta=["疗效", "心脏毒性", "肝毒性", "肾毒性", "免疫原性"],
            fill="toself", name="当前方案", line=dict(color="#F18F01")))
        fig3.add_trace(go.Scatterpolar(
            r=[50, 30, 30, 30, 30],
            theta=["疗效", "心脏毒性", "肝毒性", "肾毒性", "免疫原性"],
            fill="toself", name="安全基线", line=dict(color="#999999", dash="dot")))
        fig3.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                           height=440, template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)
        
        risk = max(cardio, hepato, nephro)
        if risk > 70:
            st.error(f"🔴 **高风险**：最大毒性评分 {risk:.1f}，建议降低剂量或更换药物。")
        elif risk > 45:
            st.warning(f"🟡 **中等风险**：最大毒性评分 {risk:.1f}，需密切监测肝肾功能。")
        else:
            st.success(f"🟢 **低风险**：最大毒性评分 {risk:.1f}，安全性良好。")
    
    with tab4:
        st.markdown(f"**Monte Carlo 群体模拟（n=1000 虚拟患者）**")
        fig4 = go.Figure()
        fig4.add_trace(go.Histogram(x=pop_effect, nbinsx=40,
                                    marker_color="#2E86AB", name="个体效应"))
        fig4.add_vline(x=50, line_dash="dash", line_color="green",
                       annotation_text="有效阈值")
        fig4.update_layout(xaxis_title="个体治疗效应 (%)", yaxis_title="患者人数",
                           height=420, template="plotly_white")
        st.plotly_chart(fig4, use_container_width=True)
        
        df = pd.DataFrame({
            "统计指标": ["平均效应", "效应中位数", "有效率(>50%)", "毒性风险率", "95%置信区间"],
            "数值": [f"{pop_effect.mean():.1f}%", f"{np.median(pop_effect):.1f}%",
                    f"{eff_rate:.1f}%", f"{tox_rate:.1f}%",
                    f"{np.percentile(pop_effect,2.5):.1f}% ~ {np.percentile(pop_effect,97.5):.1f}%"]
        })
        st.table(df)
        st.caption("通过引入体重、代谢率的随机分布，模拟真实人群的个体差异。"
                   "这正是数字孪生相比传统单一样本实验的优势所在。")

else:
    st.info("👈 请在左侧设置仿真参数，然后点击「启动AI虚拟仿真」按钮")

st.divider()

# ============ 底部说明 ============
st.header("🔬 为什么选择数字孪生试药？")
col1, col2, col3 = st.columns(3)
col1.markdown("### ⚡ 降本增效")
col1.write("传统新药研发平均耗时10年、耗资10亿美元。AI虚拟试药可以在几天内筛选数亿个分子，将早期研发周期大幅缩短。")
col2.markdown("### 🛡️ 规避风险")
col2.write("在计算机中预测毒副作用，避免受试者暴露在未知风险中，减少临床试验失败造成的损失。")
col3.markdown("### 🎯 个性化医疗")
col3.write("为每位患者构建专属的数字孪生，根据年龄、体重、基因型调整给药方案，实现精准用药。")
