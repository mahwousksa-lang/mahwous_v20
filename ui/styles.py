"""
مهووس v21 — الأنماط البصرية الكاملة
"""

def inject_css():
    import streamlit as st
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
ِ
* { font-family: 'Cairo', sans-serif !important; }

.main, .stApp {
    background: #0F1117 !important;
    color: #FAFAFA !important;
}

.block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1400px !important;
}

.stSidebar {
    background: #141824 !important;
    border-right: 1px solid #2A3042;
}

.stSidebar [data-testid="stFileUploader"] {
    background: #1E2436;
    border-radius: 12px;
    padding: 8px;
}

/* Header */
.mahwous-header {
    background: linear-gradient(135deg, #1a1f3a 0%, #0d1117 50%, #1a2a1a 100%);
    border: 1px solid #2A3042;
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6C63FF, #4ade80, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 4px;
}

.header-badge {
    background: rgba(108,99,255,0.15);
    border: 1px solid #6C63FF;
    border-radius: 20px;
    padding: 4px 16px;
    color: #a5b4fc;
    font-size: 0.8rem;
}

/* Stats */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin: 20px 0;
    direction: rtl;
}

@media(max-width:1200px) {
    .stat-grid { grid-template-columns: repeat(3, 1fr); }
}

@media(max-width:768px) {
    .stat-grid { grid-template-columns: repeat(2, 1fr); }
}

.stat-card {
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    border: 1px solid;
    transition: transform .2s;
    cursor: default;
}

.stat-card:hover { transform: translateY(-3px); }

.stat-card.red { background: rgba(248,113,113,.1); border-color: rgba(248,113,113,.3); }
.stat-card.green { background: rgba(74,222,128,.1); border-color: rgba(74,222,128,.3); }
.stat-card.blue { background: rgba(96,165,250,.1); border-color: rgba(96,165,250,.3); }
.stat-card.yellow { background: rgba(251,191,36,.1); border-color: rgba(251,191,36,.3); }
.stat-card.purple { background: rgba(167,139,250,.1); border-color: rgba(167,139,250,.3); }
.stat-card.cyan { background: rgba(34,211,238,.1); border-color: rgba(34,211,238,.3); }

.stat-card .number {
    font-size: 2rem;
    font-weight: 800;
}

.stat-card.red .number { color: #f87171; }
.stat-card.green .number { color: #4ade80; }
.stat-card.blue .number { color: #60a5fa; }
.stat-card.yellow .number { color: #fbbf24; }
.stat-card.purple .number { color: #a78bfa; }
.stat-card.cyan .number { color: #22d3ee; }

.stat-card .label {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 4px;
}

/* Product Card */
.pcard {
    background: #1a1f35;
    border: 1px solid #2A3042;
    border-radius: 16px;
    margin: 12px 0;
    overflow: hidden;
    direction: rtl;
    transition: box-shadow .2s;
}

.pcard:hover {
    box-shadow: 0 4px 20px rgba(108,99,255,.2);
}

.pcard-header {
    padding: 16px 20px 12px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid #2A3042;
}

.pcard-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #e2e8f0;
}

.pcard-brand {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 3px;
}

.pcard-body {
    padding: 16px 20px;
}

.my-price-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
    padding: 10px 16px;
    background: rgba(108,99,255,.08);
    border-radius: 10px;
}

.my-price-label {
    color: #64748b;
    font-size: 0.85rem;
}

.my-price-val {
    font-size: 1.4rem;
    font-weight: 800;
    color: #a5b4fc;
}

.my-price-diff {
    font-size: 0.8rem;
    padding: 2px 8px;
    border-radius: 8px;
}

.diff-pos { background: rgba(248,113,113,.15); color: #f87171; }
.diff-neg { background: rgba(74,222,128,.15); color: #4ade80; }
.diff-eq { background: rgba(96,165,250,.15); color: #60a5fa; }

.comp-grid { display: grid; gap: 10px; }

.comp-cell {
    background: #111827;
    border: 1px solid #374151;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: center;
    transition: border-color .2s;
}

.comp-cell:hover { border-color: #6C63FF; }

.comp-cell.lowest {
    border-color: #4ade80 !important;
    background: rgba(74,222,128,.05);
}

.comp-cell.highest {
    border-color: #f87171 !important;
    background: rgba(248,113,113,.05);
}

.comp-name {
    font-size: 0.75rem;
    color: #64748b;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.comp-price {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
}

.comp-diff {
    font-size: 0.7rem;
    margin-top: 2px;
}

/* Price Bar */
.price-bar-wrap { margin: 14px 0 10px; direction: ltr; }

.price-bar-track {
    height: 8px;
    background: #1f2937;
    border-radius: 4px;
    position: relative;
    margin: 8px 0;
}

.price-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #4ade80, #6C63FF, #f87171);
}

.price-bar-marker {
    position: absolute;
    top: -4px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 2px solid #fff;
    background: #6C63FF;
    transform: translateX(-50%);
}

.price-summary {
    display: flex;
    justify-content: space-between;
    font-size: 0.78rem;
    color: #64748b;
    direction: rtl;
}

/* Recommendations */
.recommendation {
    margin-top: 12px;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 0.85rem;
    direction: rtl;
}

.rec-lower {
    background: rgba(248,113,113,.1);
    border-right: 3px solid #f87171;
    color: #f87171;
}

.rec-raise {
    background: rgba(74,222,128,.1);
    border-right: 3px solid #4ade80;
    color: #4ade80;
}

.rec-ok {
    background: rgba(96,165,250,.1);
    border-right: 3px solid #60a5fa;
    color: #60a5fa;
}

/* Info/Warning/Success/Error Boxes */
.info-box {
    background: rgba(96,165,250,.08);
    border: 1px solid rgba(96,165,250,.25);
    border-radius: 12px;
    padding: 12px 16px;
    color: #cbd5e1;
    direction: rtl;
    margin: 8px 0;
}

.warning-box {
    background: rgba(251,191,36,.08);
    border: 1px solid rgba(251,191,36,.25);
    border-radius: 12px;
    padding: 12px 16px;
    color: #fde68a;
    direction: rtl;
    margin: 8px 0;
}

.success-box {
    background: rgba(74,222,128,.08);
    border: 1px solid rgba(74,222,128,.25);
    border-radius: 12px;
    padding: 12px 16px;
    color: #bbf7d0;
    direction: rtl;
    margin: 8px 0;
}

.error-box {
    background: rgba(248,113,113,.08);
    border: 1px solid rgba(248,113,113,.25);
    border-radius: 12px;
    padding: 12px 16px;
    color: #fecaca;
    direction: rtl;
    margin: 8px 0;
}

.ai-box {
    background: rgba(167,139,250,.08);
    border: 1px solid rgba(167,139,250,.25);
    border-radius: 12px;
    padding: 12px 16px;
    color: #ddd6fe;
    direction: rtl;
    margin: 8px 0;
}

/* History entries */
.history-entry {
    display: flex;
    gap: 16px;
    align-items: center;
    padding: 10px 16px;
    background: #1a1f35;
    border-radius: 10px;
    margin: 6px 0;
    direction: rtl;
    border: 1px solid #2A3042;
}

.history-entry .date {
    color: #475569;
    font-size: 0.75rem;
    white-space: nowrap;
}

/* Progress */
.progress-container {
    background: #1a1f35;
    border: 1px solid #2A3042;
    border-radius: 16px;
    padding: 20px;
    margin: 16px 0;
    direction: rtl;
}

.progress-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid #1f2937;
}

.progress-step:last-child { border-bottom: none; }

.step-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
}

.step-done { background: rgba(74,222,128,.2); color: #4ade80; }
.step-active { background: rgba(108,99,255,.2); color: #a5b4fc; animation: pulse 1s infinite; }
.step-pending { background: rgba(100,116,139,.1); color: #475569; }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }

/* Sidebar stats */
.sidebar-stat {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid #1f2937;
    font-size: 0.82rem;
}

.sidebar-stat .val {
    font-weight: 700;
    color: #a5b4fc;
}

/* Section card */
.section-card {
    background: #1a1f35;
    border: 1px solid #2A3042;
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
    direction: rtl;
}

.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 12px;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 48px;
    color: #475569;
}

.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 12px;
}

.empty-state .text {
    font-size: 1rem;
}

/* AI badge */
.ai-badge {
    background: linear-gradient(135deg, rgba(167,139,250,.2), rgba(96,165,250,.2));
    border: 1px solid rgba(167,139,250,.4);
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 0.7rem;
    color: #c4b5fd;
}

/* Buttons */
.stButton button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all .2s !important;
}

.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,.3) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: rgba(108,99,255,.2) !important;
    color: #a5b4fc !important;
}

/* Hide streamlit default */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

</style>
""", unsafe_allow_html=True)

