import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import platform

# --- 🛠️ 字型設定 (跨平台相容版) ---
system_name = platform.system()
if system_name == "Windows":
    # 船長的電腦
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
else:
    # Streamlit 雲端電腦 (Linux)
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']

plt.rcParams['axes.unicode_minus'] = False # 讓負號 (-) 也能正常顯示

# --- 網頁設定 ---
st.set_page_config(page_title="黑潮航海家：進階版", layout="wide")

st.title("🌊 黑潮航海家 (B4a1a)")
st.markdown("### 史前南島獨木舟：風帆向量與力矩物理模擬器 v2.1")
st.markdown("---")

# --- 側邊欄：輸入參數 ---
st.sidebar.header("⚙️ 參數設定 (Experiment Settings)")

# 1. 自變項：風帆設定
st.sidebar.subheader("1. 風帆變項 (Sail Specs)")

# 1-1. 風帆形狀
sail_shape = st.sidebar.selectbox(
    "風帆形狀 (Shape)", 
    ["倒三角形 (南島蟹爪帆)", "正方形 (古歐洲帆)", "長方形 (高瘦帆)", "直角三角形 (現代帆)"],
    help="不同形狀決定了受力中心(CoE)的高度與氣動特性"
)

# 1-2. 風帆材質
sail_material_name = st.sidebar.selectbox(
    "風帆材質 (Material)",
    ["林投葉編織 (透氣/古法)", "棉布帆 (傳統)", "現代尼龍帆 (不透氣/高效)"],
    help="材質越緻密，抓風效率越好，但也承受更大壓力"
)

sail_area = st.sidebar.slider("風帆總面積 (m²)", 2.0, 10.0, 5.0, 0.5)
wind_speed = st.sidebar.slider("風速 (m/s)", 0.0, 20.0, 10.0, 0.5, help="模擬東北季風強度")
angle_attack = st.sidebar.slider("風帆攻角 (度)", 0, 90, 60, help="風與帆面的夾角")

# 2. 控制變項：船體設定
st.sidebar.subheader("2. 船體與浮桿 (Hull & Outrigger)")

hull_options = {
    "輕木/巴爾薩木 (密度 150)": 150,
    "台灣杉木 (密度 450)": 450,
    "樟木 (密度 550)": 550,
    "竹子複合材 (密度 600)": 600,
    "現代玻纖 (密度 1500)": 1500
}
hull_label = st.sidebar.selectbox("船體材質", list(hull_options.keys()))
hull_density = hull_options[hull_label]

hull_len = st.sidebar.number_input("船長 (m)", 3.0, 10.0, 5.0)
outrigger_dist = st.sidebar.slider("浮桿距離/力臂 (m)", 1.0, 4.0, 2.0, 0.1, help="抗衡力矩的關鍵")
float_vol = st.sidebar.number_input("浮木體積 (m³)", 0.01, 0.5, 0.05, 0.01)

# --- 物理引擎 (Physics Engine) ---

AIR_DENSITY = 1.225
WATER_DENSITY = 1000
G = 9.8

# 1. 材質係數
if "林投葉" in sail_material_name:
    material_efficiency = 0.85 
elif "棉布" in sail_material_name:
    material_efficiency = 1.0  
else: 
    material_efficiency = 1.15 

# 2. 形狀係數
base_width_approx = 2.0
height_approx = sail_area / base_width_approx

if "倒三角形" in sail_shape:
    lever_arm_coeff = 0.4   
    shape_lift_eff = 1.2    
    shape_drag_coeff = 0.8  
elif "正方形" in sail_shape:
    lever_arm_coeff = 0.5   
    shape_lift_eff = 1.0    
    shape_drag_coeff = 1.0  
elif "長方形" in sail_shape:
    lever_arm_coeff = 0.6   
    shape_lift_eff = 0.9    
    shape_drag_coeff = 1.1  
else: 
    lever_arm_coeff = 0.45  
    shape_lift_eff = 1.3    
    shape_drag_coeff = 0.6  

coe_height = height_approx * lever_arm_coeff

# 3. 計算力
raw_wind_force = 0.5 * AIR_DENSITY * sail_area * (wind_speed ** 2) * material_efficiency

# 4. 向量分解
rad = math.radians(angle_attack)
force_forward = raw_wind_force * math.sin(rad) * shape_lift_eff 
force_side = raw_wind_force * math.cos(rad) * shape_drag_coeff 

# 5. 計算力矩
torque_heeling = force_side * coe_height 
buoyancy_force = float_vol * WATER_DENSITY * G
torque_righting = buoyancy_force * outrigger_dist

# --- 視覺化與輸出 ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 向量與材質分析")
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(0, 0, color='black', s=100, label='船身')
    
    ax.arrow(0, 0, force_side, 0, head_width=force_side*0.05, fc='red', ec='red', label='側推力 (Fy)')
    ax.arrow(0, 0, 0, force_forward, head_width=force_forward*0.05, fc='green', ec='green', label='前進力 (Fx)')
    ax.arrow(0, 0, force_side, force_forward, head_width=force_forward*0.05, fc='blue', ec='blue', linestyle='--', alpha=0.5, label='合力')
    
    limit = max(force_side, force_forward, 10) * 1.2
    ax.set_xlim(-limit*0.1, limit)
    ax.set_ylim(-limit*0.1, limit)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right')
    ax.set_title(f"材質: {sail_material_name} | 形狀: {sail_shape}")
    st.pyplot(fig)

with col2:
    st.subheader("⚖️ 力矩平衡 (安全檢測)")
    
    is_safe = torque_righting > torque_heeling
    status_text = "✅ 安全航行" if is_safe else "❌ 翻船警告 (CAPSIZE!)"
    color = "green" if is_safe else "red"
    st.markdown(f"## <span style='color:{color}'>{status_text}</span>", unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    m1.metric("翻覆力矩", f"{torque_heeling:.1f} N·m", f"施力臂 {coe_height:.2f} m", delta_color="inverse")
    m2.metric("抗衡力矩", f"{torque_righting:.1f} N·m", f"浮桿 {outrigger_dist} m")
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    bars = ax2.bar(["翻覆力矩", "抗衡力矩"], [torque_heeling, torque_righting], color=['red', 'green'])
    ax2.set_title("力矩對決")
    for bar in bars:
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{bar.get_height():.1f}', ha='center', va='bottom')
    st.pyplot(fig2)

st.markdown("---")
st.subheader("📝 物理觀念解析")

if not is_safe:
    st.error(f"**【翻船分析】**：您選擇的 **{sail_shape}** 重心可能太高，或者 **{sail_material_name}** 受力太強。建議：\n1. 換成倒三角形帆降低重心。\n2. 增加浮桿距離 (增加抗力臂)。\n3. 使用透氣材質洩掉部分風力。")
else:
    st.success(f"**【航行分析】**：船體穩定！**{hull_label}** 配合目前的風帆配置，成功抵抗了側風力矩。前進分力達到 {force_forward:.1f} N，效率良好。")

