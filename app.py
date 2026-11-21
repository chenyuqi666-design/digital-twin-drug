import streamlit as st
import pandas as pd
import time

# 1. 网页基础配置
st.set_page_config(page_title="数字孪生器官：AI虚拟试药", page_icon="🧬", layout="wide")

# 2. 头部标题与简介
st.title("🧬 数字孪生器官：AI能在虚拟人体里试药吗？")
st.markdown("""
在传统的药物研发中，往往需要经历漫长的动物实验和人体临床试验。而现在，借助**数字孪生技术（Digital Twins）**和**人工智能**，科学家可以在超级计算机里构建一个与真实人体器官高度一致的“虚拟替身”。
在这个虚拟器官上，AI 可以模拟药物分子的进入、与靶点的结合以及引发的生理反应，从而提前筛选出有效药物并预测毒副作用。
""")

st.divider()

# 3. 交互式模块：虚拟试药模拟器
st.subheader("🧪 虚拟试药模拟器 (In Silico Trial)")
st.caption("调整下方参数，模拟不同药物在数字孪生心脏上的反应：")

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    # 模拟药物参数输入
    drug_name = st.selectbox("选择候选药物分子", ["Drug-A (靶向药)", "Drug-B (化疗药)", "Drug-C (实验性药物)"])
    dose = st.slider("给药剂量 (mg/kg)", min_value=10, max_value=100, value=50, step=10)

    # 模拟按钮
    run_btn = st.button("🚀 启动 AI 虚拟仿真")

with col2:
    st.markdown("**📊 仿真结果面板**")
    # 占位符，用于后续动态显示结果
    result_placeholder = st.empty()

# 4. 仿真逻辑与结果展示
if run_btn:
    with st.spinner("AI 正在计算药物分子与虚拟细胞受体的结合动力学..."):
        time.sleep(2)  # 模拟计算耗时

        # 简单的模拟逻辑：根据剂量和药物类型生成结果
        efficacy = min(95, int(dose * 0.8 + (10 if "A" in drug_name else 0)))
        toxicity = min(100, int(dose * 0.5 + (20 if "C" in drug_name else 0)))

        # 生成结果数据
        df_result = pd.DataFrame({
            "评估指标": ["预期疗效 (%)", "毒副作用风险 (%)", "临床试验推荐度"],
            "数值": [f"{efficacy}%", f"{toxicity}%", "高" if efficacy > 60 and toxicity < 40 else "低"]
        })

        # 更新结果面板
        result_placeholder.dataframe(df_result, use_container_width=True)

        if efficacy > 60 and toxicity < 40:
            st.success("✅ 仿真结论：该药物在数字孪生器官中表现出良好的疗效与安全性平衡，建议进入下一阶段实体类器官验证。")
        else:
            st.warning("⚠️ 仿真结论：该药物可能引发较高的心脏毒性或疗效不足，建议调整分子结构或降低剂量。")

st.divider()

# 5. 底部拓展信息
st.subheader("🔬 为什么选择数字孪生试药？")
tabs = st.tabs(["⏱️ 降本增效", "🛡️ 规避风险", "👤 个性化医疗"])

with tabs[0]:
    st.markdown("传统新药研发平均耗时10年、耗资10亿美元。AI 虚拟试药可以在几天内筛选数亿个分子，将早期研发周期大幅缩短。")
with tabs[1]:
    st.markdown("在虚拟器官上提前预测心律失常等严重不良反应，减少动物实验的伦理争议，避免无效药物进入人体临床试验。")
with tabs[2]:
    st.markdown(
        "未来，每个人都可以拥有基于自身基因和病历数据的“数字分身”，医生可以在你的数字分身身上测试各种治疗方案，实现真正的精准医疗。")