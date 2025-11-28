"""
Piecewise (Segmented) Regression Analysis - Streamlit Application
Based on Muggeo's Algorithm (2003)
Author: Merwan Roudane
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import piecewise_regression
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Piecewise Regression Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    /* Headers */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-header h1 {
        color: white;
        text-align: center;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: #e0e0e0;
        text-align: center;
        font-size: 1.1rem;
        margin-top: 10px;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #e8f4f8 0%, #d4e8ed 100%);
        border-left: 5px solid #17a2b8;
        padding: 15px 20px;
        border-radius: 0 10px 10px 0;
        margin: 15px 0;
    }
    
    /* Success box */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
        padding: 15px 20px;
        border-radius: 0 10px 10px 0;
        margin: 15px 0;
    }
    
    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        border-left: 5px solid #ffc107;
        padding: 15px 20px;
        border-radius: 0 10px 10px 0;
        margin: 15px 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #667eea;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1e3c72;
    }
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    
    /* Formula box */
    .formula-box {
        background: linear-gradient(135deg, #fff9e6 0%, #fff3cc 100%);
        border: 2px solid #f0ad4e;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
    }
    
    /* Theory section */
    .theory-section {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    /* Results table */
    .results-table {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 3px 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>📊 Piecewise (Segmented) Regression Analysis</h1>
    <p>Based on Muggeo's Iterative Algorithm (2003) | Detect Structural Breakpoints in Your Data</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🎛️ Analysis Settings")
    st.markdown("---")
    
    # File upload
    st.markdown("### 📁 Data Upload")
    uploaded_file = st.file_uploader(
        "Upload Excel File (.xlsx)",
        type=['xlsx', 'xls'],
        help="Upload your data file with X and Y variables"
    )
    
    st.markdown("---")
    
    # Analysis options
    st.markdown("### ⚙️ Model Parameters")
    
    analysis_mode = st.radio(
        "Analysis Mode",
        ["Single Breakpoint Model", "Multiple Breakpoints", "Model Selection (BIC)"],
        help="Choose how to determine the number of breakpoints"
    )
    
    if analysis_mode == "Single Breakpoint Model":
        n_breakpoints = 1
    elif analysis_mode == "Multiple Breakpoints":
        n_breakpoints = st.slider(
            "Number of Breakpoints",
            min_value=1, max_value=5, value=2,
            help="Specify the number of breakpoints to fit"
        )
    else:
        max_breakpoints = st.slider(
            "Maximum Breakpoints to Test",
            min_value=2, max_value=8, value=5,
            help="Test models with 0 to N breakpoints"
        )
    
    st.markdown("---")
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        n_boot = st.slider(
            "Bootstrap Iterations",
            min_value=0, max_value=200, value=100,
            help="Number of bootstrap restarting iterations"
        )
        
        max_iterations = st.slider(
            "Max Muggeo Iterations",
            min_value=10, max_value=100, value=30,
            help="Maximum iterations for convergence"
        )
        
        tolerance = st.select_slider(
            "Convergence Tolerance",
            options=[1e-3, 1e-4, 1e-5, 1e-6, 1e-7],
            value=1e-5,
            help="Tolerance for breakpoint convergence"
        )
        
        min_distance_bp = st.slider(
            "Min Distance Between BPs (%)",
            min_value=1, max_value=10, value=1,
            help="Minimum distance between breakpoints as % of data range"
        ) / 100
        
        min_distance_edge = st.slider(
            "Min Distance from Edge (%)",
            min_value=1, max_value=10, value=2,
            help="Minimum distance from data edge as % of range"
        ) / 100
    
    st.markdown("---")
    st.markdown("### 📚 References")
    st.markdown("""
    - Muggeo (2003) *Statistics in Medicine*
    - Davies (1987) *Biometrika*
    - [piecewise-regression](https://github.com/chasmani/piecewise-regression)
    """)

# ==================== MAIN CONTENT ====================
# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Theory & Methodology", 
    "📊 Data Analysis", 
    "📈 Results & Visualization",
    "📋 Model Comparison"
])

# ==================== TAB 1: THEORY ====================
with tab1:
    st.markdown('<div class="section-header">📖 Piecewise Regression: Theory & Methodology</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="theory-section">', unsafe_allow_html=True)
        st.markdown("### 🎯 What is Piecewise Regression?")
        st.markdown("""
        **Piecewise regression** (also called *segmented regression* or *broken-line regression*) 
        is a statistical technique that fits multiple linear models to different segments of data, 
        connected at unknown **breakpoints** (change points).
        
        This method is particularly useful for:
        - Detecting **structural changes** in time series
        - Identifying **regime shifts** in economic data
        - Modeling **threshold effects** in biological systems
        - Analyzing **policy impacts** with unknown timing
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("### 📐 Mathematical Model")
        st.latex(r"""
        y_i = \beta_0 + \beta_1 x_i + \sum_{k=1}^{K} \delta_k (x_i - \psi_k)_+ + \varepsilon_i
        """)
        st.markdown("""
        **Where:**
        - $y_i$ = dependent variable
        - $x_i$ = independent variable  
        - $\\beta_0$ = intercept (constant)
        - $\\beta_1$ = initial slope (α₁)
        - $\\psi_k$ = breakpoint locations (unknown)
        - $\\delta_k$ = change in slope at breakpoint k (βₖ)
        - $(x - \\psi)_+ = \\max(0, x - \\psi)$ (positive part function)
        - $\\varepsilon_i$ = error term
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="theory-section">', unsafe_allow_html=True)
        st.markdown("### 🔄 Muggeo's Algorithm")
        st.markdown("""
        The algorithm uses an **iterative linearization** approach:
        
        **Step 1:** Initialize breakpoint guesses $\\psi^{(0)}$
        
        **Step 2:** Linearize the model using Taylor expansion:
        """)
        st.latex(r"""
        (x - \psi)_+ \approx (x - \psi^{(0)})_+ - I(x > \psi^{(0)}) \cdot (\psi - \psi^{(0)})
        """)
        st.markdown("""
        **Step 3:** Fit augmented linear model:
        """)
        st.latex(r"""
        y = \beta_0 + \beta_1 x + \sum_k \left[ \delta_k U_k + \gamma_k V_k \right] + \varepsilon
        """)
        st.markdown("""
        Where:
        - $U_k = (x - \\psi_k^{(0)})_+$
        - $V_k = I(x > \\psi_k^{(0)})$
        
        **Step 4:** Update breakpoints:
        """)
        st.latex(r"\psi_k^{(new)} = \psi_k^{(old)} - \frac{\hat{\gamma}_k}{\hat{\delta}_k}")
        st.markdown("""
        **Step 5:** Repeat until convergence
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional theory
    st.markdown('<div class="section-header">📊 Statistical Tests & Model Selection</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### 🧪 Davies Test")
        st.markdown("""
        The **Davies test** (1987) tests for the existence of at least one breakpoint:
        
        **Null Hypothesis:** $H_0: \\delta = 0$ (no breakpoint)
        
        **Alternative:** $H_1: \\delta \\neq 0$ (breakpoint exists)
        
        The test handles the **nuisance parameter problem** where the breakpoint 
        location only exists under the alternative hypothesis.
        """)
        st.latex(r"p \approx \Phi(-M) + V \cdot \frac{e^{-M^2/2}}{\sqrt{8\pi}}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### 📉 Model Selection (BIC)")
        st.markdown("""
        The **Bayesian Information Criterion** helps select the optimal number of breakpoints:
        """)
        st.latex(r"BIC = n \cdot \ln\left(\frac{RSS}{n}\right) + k \cdot \ln(n)")
        st.markdown("""
        **Where:**
        - $n$ = number of observations
        - $RSS$ = residual sum of squares
        - $k$ = number of parameters = $2 + 2K$ (K = breakpoints)
        
        **Lower BIC = Better Model**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Confidence intervals
    st.markdown('<div class="theory-section">', unsafe_allow_html=True)
    st.markdown("### 📏 Standard Errors & Confidence Intervals")
    
    col5, col6 = st.columns([1, 1])
    
    with col5:
        st.markdown("**Breakpoint Standard Error (Delta Method):**")
        st.latex(r"""
        SE(\hat{\psi}) = \frac{1}{|\hat{\delta}|} \sqrt{Var(\hat{\gamma}) + \frac{\hat{\gamma}^2}{\hat{\delta}^2}Var(\hat{\delta}) - 2\frac{\hat{\gamma}}{\hat{\delta}}Cov(\hat{\gamma}, \hat{\delta})}
        """)
    
    with col6:
        st.markdown("**Slope Standard Error:**")
        st.latex(r"""
        SE(\hat{\alpha}_k) = \sqrt{\sum_{i,j \leq k} Cov(\hat{\beta}_i, \hat{\beta}_j)}
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 2: DATA ANALYSIS ====================
with tab2:
    st.markdown('<div class="section-header">📊 Data Analysis</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Read data
        try:
            df = pd.read_excel(uploaded_file)
            st.session_state['data'] = df
            
            st.markdown('<div class="success-box">✅ Data loaded successfully!</div>', unsafe_allow_html=True)
            
            # Data preview
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📋 Data Preview")
                st.dataframe(df.head(20), use_container_width=True, height=400)
            
            with col2:
                st.markdown("### 📊 Data Summary")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(df)}</div>
                    <div class="metric-label">Observations</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card" style="margin-top: 15px;">
                    <div class="metric-value">{len(df.columns)}</div>
                    <div class="metric-label">Variables</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 🔢 Numeric Columns")
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                for col in numeric_cols[:10]:
                    st.markdown(f"• **{col}**")
            
            # Variable selection
            st.markdown("---")
            st.markdown("### 🎯 Variable Selection")
            
            col_x, col_y = st.columns(2)
            
            with col_x:
                x_var = st.selectbox(
                    "Select X Variable (Independent)",
                    options=numeric_cols,
                    help="This is typically time or the explanatory variable"
                )
            
            with col_y:
                y_var = st.selectbox(
                    "Select Y Variable (Dependent)",
                    options=[c for c in numeric_cols if c != x_var],
                    help="This is the response variable you want to analyze"
                )
            
            # Store selections
            st.session_state['x_var'] = x_var
            st.session_state['y_var'] = y_var
            
            # Show scatter plot
            if x_var and y_var:
                st.markdown("### 📈 Data Visualization")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df[x_var],
                    y=df[y_var],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=df[x_var],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title=x_var)
                    ),
                    name='Data Points',
                    hovertemplate=f'{x_var}: %{{x}}<br>{y_var}: %{{y}}<extra></extra>'
                ))
                
                fig.update_layout(
                    title=dict(
                        text=f'<b>{y_var}</b> vs <b>{x_var}</b>',
                        font=dict(size=20)
                    ),
                    xaxis_title=x_var,
                    yaxis_title=y_var,
                    template='plotly_white',
                    height=500,
                    hovermode='closest'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Run analysis button
                st.markdown("---")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    run_analysis = st.button("🚀 Run Piecewise Regression Analysis", use_container_width=True)
                
                if run_analysis:
                    with st.spinner("Running analysis... This may take a moment."):
                        # Prepare data
                        xx = df[x_var].values
                        yy = df[y_var].values
                        
                        # Remove NaN
                        mask = ~(np.isnan(xx) | np.isnan(yy))
                        xx = xx[mask]
                        yy = yy[mask]
                        
                        # Sort by x
                        sort_idx = np.argsort(xx)
                        xx = xx[sort_idx]
                        yy = yy[sort_idx]
                        
                        try:
                            if analysis_mode == "Model Selection (BIC)":
                                # Run model selection
                                results = {}
                                model_comparison = []
                                
                                progress_bar = st.progress(0)
                                
                                for k in range(0, max_breakpoints + 1):
                                    progress_bar.progress((k + 1) / (max_breakpoints + 1))
                                    
                                    if k == 0:
                                        # Simple linear regression
                                        import statsmodels.api as sm
                                        X = sm.add_constant(xx)
                                        model = sm.OLS(yy, X).fit()
                                        rss = np.sum(model.resid ** 2)
                                        n = len(xx)
                                        bic = n * np.log(rss / n) + 2 * np.log(n)
                                        model_comparison.append({
                                            'n_breakpoints': 0,
                                            'BIC': bic,
                                            'RSS': rss,
                                            'R²': model.rsquared,
                                            'Converged': True
                                        })
                                    else:
                                        pw_fit = piecewise_regression.Fit(
                                            xx, yy,
                                            n_breakpoints=k,
                                            n_boot=n_boot,
                                            max_iterations=max_iterations,
                                            tolerance=tolerance,
                                            min_distance_between_breakpoints=min_distance_bp,
                                            min_distance_to_edge=min_distance_edge,
                                            verbose=False
                                        )
                                        res = pw_fit.get_results()
                                        
                                        if res['converged']:
                                            model_comparison.append({
                                                'n_breakpoints': k,
                                                'BIC': res['bic'],
                                                'RSS': res['rss'],
                                                'R²': pw_fit.best_muggeo.best_fit.r_squared if pw_fit.best_muggeo else None,
                                                'Converged': True
                                            })
                                            results[k] = pw_fit
                                        else:
                                            model_comparison.append({
                                                'n_breakpoints': k,
                                                'BIC': None,
                                                'RSS': None,
                                                'R²': None,
                                                'Converged': False
                                            })
                                
                                progress_bar.empty()
                                
                                st.session_state['model_comparison'] = model_comparison
                                st.session_state['all_models'] = results
                                
                                # Find best model
                                converged_models = [m for m in model_comparison if m['Converged'] and m['BIC'] is not None]
                                if converged_models:
                                    best_model = min(converged_models, key=lambda x: x['BIC'])
                                    best_k = best_model['n_breakpoints']
                                    
                                    if best_k == 0:
                                        st.session_state['best_fit'] = None
                                        st.session_state['best_k'] = 0
                                    else:
                                        st.session_state['best_fit'] = results[best_k]
                                        st.session_state['best_k'] = best_k
                                
                            else:
                                # Single model fit
                                pw_fit = piecewise_regression.Fit(
                                    xx, yy,
                                    n_breakpoints=n_breakpoints,
                                    n_boot=n_boot,
                                    max_iterations=max_iterations,
                                    tolerance=tolerance,
                                    min_distance_between_breakpoints=min_distance_bp,
                                    min_distance_to_edge=min_distance_edge,
                                    verbose=False
                                )
                                
                                st.session_state['pw_fit'] = pw_fit
                                st.session_state['xx'] = xx
                                st.session_state['yy'] = yy
                            
                            st.success("✅ Analysis completed! Go to **Results & Visualization** tab.")
                            
                        except Exception as e:
                            st.error(f"❌ Error during analysis: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    else:
        st.markdown('<div class="warning-box">⚠️ Please upload an Excel file (.xlsx) to begin analysis.</div>', unsafe_allow_html=True)
        
        # Demo data option
        st.markdown("### 🎮 Or Use Demo Data")
        if st.button("Generate Demo Data"):
            np.random.seed(42)
            n_points = 150
            
            # Create data with 2 breakpoints
            xx = np.linspace(0, 100, n_points)
            bp1, bp2 = 30, 70
            
            yy = (50 + 
                  0.8 * xx + 
                  -1.5 * np.maximum(xx - bp1, 0) + 
                  1.2 * np.maximum(xx - bp2, 0) + 
                  np.random.normal(0, 3, n_points))
            
            demo_df = pd.DataFrame({'X': xx, 'Y': yy})
            st.session_state['data'] = demo_df
            st.session_state['x_var'] = 'X'
            st.session_state['y_var'] = 'Y'
            
            st.success("✅ Demo data generated! Refresh the page to see it.")
            st.dataframe(demo_df.head(10))

# ==================== TAB 3: RESULTS ====================
with tab3:
    st.markdown('<div class="section-header">📈 Results & Visualization</div>', unsafe_allow_html=True)
    
    if 'pw_fit' in st.session_state or 'best_fit' in st.session_state:
        
        # Get the fit object
        if 'best_fit' in st.session_state and st.session_state.get('best_fit') is not None:
            pw_fit = st.session_state['best_fit']
            st.markdown(f"<div class='success-box'>🏆 Best Model Selected: **{st.session_state['best_k']} Breakpoint(s)** (by BIC)</div>", unsafe_allow_html=True)
        elif 'pw_fit' in st.session_state:
            pw_fit = st.session_state['pw_fit']
        else:
            st.warning("No model fitted yet. Please run the analysis first.")
            st.stop()
        
        # Get data
        if 'data' in st.session_state:
            df = st.session_state['data']
            x_var = st.session_state.get('x_var', 'X')
            y_var = st.session_state.get('y_var', 'Y')
            xx = df[x_var].dropna().values
            yy = df[y_var].dropna().values
            mask = ~(np.isnan(xx) | np.isnan(yy))
            xx = xx[mask]
            yy = yy[mask]
            sort_idx = np.argsort(xx)
            xx = xx[sort_idx]
            yy = yy[sort_idx]
        else:
            xx = st.session_state.get('xx', np.array([]))
            yy = st.session_state.get('yy', np.array([]))
            x_var = 'X'
            y_var = 'Y'
        
        # Check convergence
        results = pw_fit.get_results()
        
        if not results['converged']:
            st.markdown('<div class="warning-box">⚠️ Algorithm did not converge. Try different parameters or number of breakpoints.</div>', unsafe_allow_html=True)
        else:
            # Display key metrics
            st.markdown("### 📊 Model Summary")
            
            estimates = results['estimates']
            n_bp = len([k for k in estimates.keys() if 'breakpoint' in k])
            
            # Metric cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{n_bp}</div>
                    <div class="metric-label">Breakpoints</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                r_sq = pw_fit.best_muggeo.best_fit.r_squared
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{r_sq:.4f}</div>
                    <div class="metric-label">R² (Explained Variance)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{results['rss']:.2f}</div>
                    <div class="metric-label">RSS</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                davies_p = results['davies']
                color = "#28a745" if davies_p < 0.05 else "#dc3545"
                st.markdown(f"""
                <div class="metric-card" style="border-top-color: {color};">
                    <div class="metric-value" style="color: {color};">{davies_p:.2e}</div>
                    <div class="metric-label">Davies Test p-value</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Interpretation
            st.markdown("---")
            if davies_p < 0.05:
                st.markdown('<div class="success-box">✅ <b>Davies Test:</b> Significant evidence for the existence of breakpoint(s) (p < 0.05). Reject null hypothesis of no breakpoints.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-box">⚠️ <b>Davies Test:</b> No significant evidence for breakpoints (p ≥ 0.05). Consider using a simple linear model.</div>', unsafe_allow_html=True)
            
            # Results table
            st.markdown("### 📋 Parameter Estimates")
            
            # Prepare results dataframe
            results_data = []
            for name, details in estimates.items():
                if isinstance(details, dict):
                    results_data.append({
                        'Parameter': name,
                        'Estimate': details.get('estimate', '-'),
                        'Std. Error': details.get('se', '-'),
                        't-statistic': details.get('t_stat', '-'),
                        'p-value': details.get('p_t', '-'),
                        'CI Lower (2.5%)': details.get('confidence_interval', ['-', '-'])[0],
                        'CI Upper (97.5%)': details.get('confidence_interval', ['-', '-'])[1]
                    })
            
            results_df = pd.DataFrame(results_data)
            
            # Format numeric columns
            for col in ['Estimate', 'Std. Error', 'CI Lower (2.5%)', 'CI Upper (97.5%)']:
                results_df[col] = results_df[col].apply(
                    lambda x: f"{x:.6f}" if isinstance(x, (int, float)) else x
                )
            
            st.dataframe(results_df, use_container_width=True, hide_index=True)
            
            # Visualization
            st.markdown("### 📈 Fitted Model Visualization")
            
            # Get breakpoints and create fitted line
            breakpoints = [estimates[f'breakpoint{i+1}']['estimate'] for i in range(n_bp)]
            const = estimates['const']['estimate']
            alpha1 = estimates['alpha1']['estimate']
            betas = [estimates[f'beta{i+1}']['estimate'] for i in range(n_bp)]
            
            # Generate fitted values
            xx_fit = np.linspace(xx.min(), xx.max(), 500)
            yy_fit = const + alpha1 * xx_fit
            for i, bp in enumerate(breakpoints):
                yy_fit += betas[i] * np.maximum(xx_fit - bp, 0)
            
            # Create plotly figure
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    '<b>Fitted Piecewise Regression</b>',
                    '<b>Residuals vs Fitted</b>',
                    '<b>Residual Distribution</b>',
                    '<b>Q-Q Plot</b>'
                ),
                specs=[[{}, {}], [{}, {}]],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # Plot 1: Main fit
            fig.add_trace(
                go.Scatter(x=xx, y=yy, mode='markers', name='Data',
                          marker=dict(size=8, color='#667eea', opacity=0.6)),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=xx_fit, y=yy_fit, mode='lines', name='Fitted Model',
                          line=dict(color='#e74c3c', width=3)),
                row=1, col=1
            )
            
            # Add breakpoint lines
            colors = ['#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
            for i, bp in enumerate(breakpoints):
                fig.add_vline(x=bp, line_dash="dash", line_color=colors[i % len(colors)],
                             annotation_text=f"BP{i+1}: {bp:.2f}", row=1, col=1)
            
            # Add confidence intervals for breakpoints
            for i, bp in enumerate(breakpoints):
                ci = estimates[f'breakpoint{i+1}']['confidence_interval']
                fig.add_vrect(x0=ci[0], x1=ci[1], fillcolor=colors[i % len(colors)],
                             opacity=0.2, line_width=0, row=1, col=1)
            
            # Plot 2: Residuals
            yy_pred = const + alpha1 * xx
            for i, bp in enumerate(breakpoints):
                yy_pred += betas[i] * np.maximum(xx - bp, 0)
            residuals = yy - yy_pred
            
            fig.add_trace(
                go.Scatter(x=yy_pred, y=residuals, mode='markers', name='Residuals',
                          marker=dict(size=8, color='#3498db', opacity=0.6)),
                row=1, col=2
            )
            fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=2)
            
            # Plot 3: Residual histogram
            fig.add_trace(
                go.Histogram(x=residuals, name='Residuals', nbinsx=30,
                            marker_color='#9b59b6', opacity=0.7),
                row=2, col=1
            )
            
            # Plot 4: Q-Q plot
            from scipy import stats
            sorted_residuals = np.sort(residuals)
            theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(residuals)))
            
            fig.add_trace(
                go.Scatter(x=theoretical_quantiles, y=sorted_residuals, mode='markers',
                          name='Q-Q', marker=dict(size=6, color='#e74c3c')),
                row=2, col=2
            )
            # Add reference line
            fig.add_trace(
                go.Scatter(x=[-3, 3], y=[-3*np.std(residuals), 3*np.std(residuals)],
                          mode='lines', line=dict(dash='dash', color='gray'),
                          showlegend=False),
                row=2, col=2
            )
            
            fig.update_layout(
                height=800,
                template='plotly_white',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            fig.update_xaxes(title_text=x_var, row=1, col=1)
            fig.update_yaxes(title_text=y_var, row=1, col=1)
            fig.update_xaxes(title_text="Fitted Values", row=1, col=2)
            fig.update_yaxes(title_text="Residuals", row=1, col=2)
            fig.update_xaxes(title_text="Residuals", row=2, col=1)
            fig.update_yaxes(title_text="Frequency", row=2, col=1)
            fig.update_xaxes(title_text="Theoretical Quantiles", row=2, col=2)
            fig.update_yaxes(title_text="Sample Quantiles", row=2, col=2)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Segment interpretation
            st.markdown("### 📝 Segment Interpretation")
            
            # Calculate slopes for each segment
            alphas = [alpha1]
            for i in range(n_bp):
                alphas.append(alphas[-1] + betas[i])
            
            segments_data = []
            segment_starts = [xx.min()] + breakpoints
            segment_ends = breakpoints + [xx.max()]
            
            for i in range(n_bp + 1):
                segments_data.append({
                    'Segment': i + 1,
                    'Start': f"{segment_starts[i]:.2f}",
                    'End': f"{segment_ends[i]:.2f}",
                    'Slope (α)': f"{alphas[i]:.4f}",
                    'Interpretation': '📈 Increasing' if alphas[i] > 0 else '📉 Decreasing' if alphas[i] < 0 else '➡️ Flat'
                })
            
            st.dataframe(pd.DataFrame(segments_data), use_container_width=True, hide_index=True)
            
            # Model equation
            st.markdown("### 📐 Estimated Model Equation")
            
            eq = f"$$\\hat{{y}} = {const:.4f} + {alpha1:.4f} \\cdot x"
            for i, (bp, beta) in enumerate(zip(breakpoints, betas)):
                sign = "+" if beta >= 0 else ""
                eq += f" {sign} {beta:.4f} \\cdot (x - {bp:.2f})_+"
            eq += "$$"
            
            st.markdown(eq)
    
    elif 'best_k' in st.session_state and st.session_state['best_k'] == 0:
        st.markdown('<div class="info-box">📊 Best model is simple linear regression (0 breakpoints). No structural breaks detected in the data.</div>', unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="warning-box">⚠️ No analysis results available. Please run the analysis in the <b>Data Analysis</b> tab first.</div>', unsafe_allow_html=True)

# ==================== TAB 4: MODEL COMPARISON ====================
with tab4:
    st.markdown('<div class="section-header">📋 Model Comparison</div>', unsafe_allow_html=True)
    
    if 'model_comparison' in st.session_state:
        model_comparison = st.session_state['model_comparison']
        
        # Create comparison dataframe
        comp_df = pd.DataFrame(model_comparison)
        
        # Highlight best model
        converged = comp_df[comp_df['Converged'] == True]
        if len(converged) > 0 and converged['BIC'].notna().any():
            best_idx = converged['BIC'].idxmin()
            best_k = comp_df.loc[best_idx, 'n_breakpoints']
            
            st.markdown(f'<div class="success-box">🏆 <b>Best Model:</b> {best_k} breakpoint(s) with BIC = {comp_df.loc[best_idx, "BIC"]:.4f}</div>', unsafe_allow_html=True)
        
        # Display table
        st.markdown("### 📊 Model Comparison Table")
        
        # Format the dataframe
        display_df = comp_df.copy()
        display_df['BIC'] = display_df['BIC'].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
        display_df['RSS'] = display_df['RSS'].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
        display_df['R²'] = display_df['R²'].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
        display_df['Converged'] = display_df['Converged'].apply(lambda x: "✅" if x else "❌")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # BIC plot
        st.markdown("### 📈 BIC Comparison")
        
        converged_df = comp_df[comp_df['Converged'] == True].dropna(subset=['BIC'])
        
        if len(converged_df) > 0:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=converged_df['n_breakpoints'],
                y=converged_df['BIC'],
                marker_color=['#28a745' if x == best_k else '#667eea' for x in converged_df['n_breakpoints']],
                text=converged_df['BIC'].round(2),
                textposition='outside',
                hovertemplate='Breakpoints: %{x}<br>BIC: %{y:.4f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(text='<b>BIC by Number of Breakpoints</b>', font=dict(size=18)),
                xaxis_title='Number of Breakpoints',
                yaxis_title='BIC (lower is better)',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # R² comparison
            if 'R²' in converged_df.columns:
                fig2 = go.Figure()
                
                fig2.add_trace(go.Scatter(
                    x=converged_df['n_breakpoints'],
                    y=converged_df['R²'],
                    mode='lines+markers',
                    marker=dict(size=12, color='#e74c3c'),
                    line=dict(width=3),
                    hovertemplate='Breakpoints: %{x}<br>R²: %{y:.4f}<extra></extra>'
                ))
                
                fig2.update_layout(
                    title=dict(text='<b>R² by Number of Breakpoints</b>', font=dict(size=18)),
                    xaxis_title='Number of Breakpoints',
                    yaxis_title='R² (higher is better)',
                    template='plotly_white',
                    height=400
                )
                
                st.plotly_chart(fig2, use_container_width=True)
    
    else:
        st.markdown('<div class="warning-box">⚠️ Run <b>Model Selection (BIC)</b> analysis to see model comparisons.</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 📖 About Model Selection
        
        When you run **Model Selection (BIC)** mode, the application will:
        
        1. Fit models with 0, 1, 2, ... K breakpoints
        2. Calculate the **Bayesian Information Criterion (BIC)** for each model
        3. Select the model with the **lowest BIC** as the best model
        
        The BIC balances model fit (lower RSS) against model complexity (more parameters), 
        helping you avoid overfitting while still capturing true structural breaks.
        """)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>Piecewise Regression Analysis Tool</strong></p>
    <p>Based on Muggeo's Algorithm (2003) | Developed with Streamlit & Python</p>
    <p>📧 Contact: merwanroudane920@gmail.com</p>
</div>
""", unsafe_allow_html=True)
