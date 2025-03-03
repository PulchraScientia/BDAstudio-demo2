import streamlit as st
import pandas as pd
import plotly.express as px
import uuid
import datetime
import json
from components.sidebar import render_sidebar
from components.materials_input import render_materials_input
from components.dataset_selector import render_dataset_selector
from components.experiment_results import render_experiment_results
from utils.sql_validator import validate_sql

# Initialize page
st.set_page_config(
    page_title="BDA Studio - Experiments",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 네비게이션 메뉴 숨기기
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
div[data-testid="stSidebarNav"] {display: none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Render sidebar
render_sidebar()

# Check if user has selected a workspace
if not st.session_state.current_workspace:
    st.warning("Please select or create a workspace first")
    st.stop()

# Initialize session state for this page
if 'experiment_tab' not in st.session_state:
    st.session_state.experiment_tab = "list"
if 'current_experiment' not in st.session_state:
    st.session_state.current_experiment = None
if 'selected_dataset' not in st.session_state:
    st.session_state.selected_dataset = None
if 'selected_material' not in st.session_state:
    st.session_state.selected_material = None
if 'navigate_to_assistant' not in st.session_state:
    st.session_state.navigate_to_assistant = False

# 페이지 전환 확인
if st.session_state.navigate_to_assistant:
    st.session_state.navigate_to_assistant = False  # 상태 재설정
    st.switch_page("pages/03_assistant.py")

# Main experiments page
st.title("Experiments")

# Tabs for different experiment functions
tabs = ["List", "Create"]

# 세션 상태에 따라 초기 탭 설정
tab_index = 0  # 기본값은 List 탭 (인덱스 0)
if st.session_state.experiment_tab == "create":
    tab_index = 1  # Create 탭 (인덱스 1)

# 탭 생성 시 초기 인덱스 설정
tab_list, tab_create = st.tabs(tabs)

# 현재 활성화된 탭에 따라 세션 상태 업데이트
# (이 부분은 탭이 변경될 때마다 세션 상태를 업데이트하는 용도)
if tab_index == 0:
    st.session_state.experiment_tab = "list"
else:
    st.session_state.experiment_tab = "create"

# Implement experiment creation tab
with tab_create:
    st.header("Create Experiment")
    
    # Dataset 선택 dropdown 추가
    all_datasets = [ds for ds in st.session_state.datasets 
                   if ds['workspace_id'] == st.session_state.current_workspace['id']]
    
    dataset_options = ["Select a dataset"] + [f"{ds['project']}.{ds['dataset']}" for ds in all_datasets]
    
    # 현재 선택된 dataset이 있으면 해당 값을 default로 설정
    default_dataset_idx = 0
    if st.session_state.selected_dataset:
        selected_ds_str = f"{st.session_state.selected_dataset['project']}.{st.session_state.selected_dataset['dataset']}"
        if selected_ds_str in dataset_options:
            default_dataset_idx = dataset_options.index(selected_ds_str)
    
    selected_dataset_str = st.selectbox(
        "Select Dataset", 
        dataset_options,
        index=default_dataset_idx
    )
    
    # 선택된 dataset으로 세션 상태 업데이트
    if selected_dataset_str != "Select a dataset":
        for ds in all_datasets:
            if f"{ds['project']}.{ds['dataset']}" == selected_dataset_str:
                st.session_state.selected_dataset = ds
                break
    else:
        st.session_state.selected_dataset = None
    
    # Material 선택 dropdown 추가
    all_materials = [m for m in st.session_state.materials 
                    if m['workspace_id'] == st.session_state.current_workspace['id']]
    
    material_options = ["Select a material"] + [m['name'] for m in all_materials]
    
    # 현재 선택된 material이 있으면 해당 값을 default로 설정
    default_material_idx = 0
    if st.session_state.selected_material:
        selected_mat_str = st.session_state.selected_material['name']
        if selected_mat_str in material_options:
            default_material_idx = material_options.index(selected_mat_str)
    
    selected_material_str = st.selectbox(
        "Select Material", 
        material_options,
        index=default_material_idx
    )
    
    # 선택된 material로 세션 상태 업데이트
    if selected_material_str != "Select a material":
        for m in all_materials:
            if m['name'] == selected_material_str:
                st.session_state.selected_material = m
                break
    else:
        st.session_state.selected_material = None
    
    # Check if dataset and material are selected
    if not st.session_state.selected_dataset:
        st.warning("Please select a dataset")
    
    if not st.session_state.selected_material:
        st.warning("Please select a material")
    
    if st.session_state.selected_dataset and st.session_state.selected_material:
        # Display current selections
        st.subheader("Selected Components")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Dataset:** {st.session_state.selected_dataset['project']}.{st.session_state.selected_dataset['dataset']}")
            st.write(f"Tables: {', '.join([t['name'] for t in st.session_state.selected_dataset['tables']])}")
        
        with col2:
            st.info(f"**Material:** {st.session_state.selected_material['name']}")
            train_set_name = st.session_state.selected_material.get('train_set_name', 'Training Set')
            test_set_name = st.session_state.selected_material.get('test_set_name', 'Test Set')
            st.write(f"Training set: {train_set_name} ({len(st.session_state.selected_material['training_set'])} samples)")
            st.write(f"Test set: {test_set_name} ({len(st.session_state.selected_material['test_set'])} samples)")
        
        # Knowledge data display (추가)
        if 'knowledge_data' in st.session_state.selected_material and st.session_state.selected_material['knowledge_data']:
            with st.expander("Knowledge Data"):
                st.write(st.session_state.selected_material['knowledge_data'])
        
        # Experiment settings
        st.subheader("Experiment Settings")
        
        exp_name = st.text_input("Experiment Name", f"Experiment-{len(st.session_state.experiments)+1}")
        exp_desc = st.text_area("Description", "Testing natural language to SQL conversion")
        
        # Advanced settings (could be expanded)
        with st.expander("Advanced Settings"):
            st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
            st.number_input("Max Tokens", min_value=100, max_value=4000, value=1000, step=100)
        
        # Create experiment button
        if st.button("Create and Run Experiment"):
            # Create a new experiment
            new_experiment = {
                "id": str(uuid.uuid4()),
                "name": exp_name,
                "description": exp_desc,
                "workspace_id": st.session_state.current_workspace['id'],
                "dataset_id": st.session_state.selected_dataset['id'] if 'id' in st.session_state.selected_dataset else None,
                "dataset": st.session_state.selected_dataset,
                "material_id": st.session_state.selected_material['id'],
                "material": st.session_state.selected_material,
                "status": "completed",  # For demo purposes, we'll set it as completed
                "results": {
                    "accuracy": 0.85,  # Mock results
                    "test_results": []
                },
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Generate mock test results
            for test_item in st.session_state.selected_material['test_set']:
                # For demo purposes, randomly mark some as correct and some as wrong
                is_correct = hash(test_item['nl']) % 4 != 0  # 75% correct rate
                
                generated_sql = test_item['sql']
                if not is_correct:
                    # Slightly modify the SQL to simulate an error
                    if "WHERE" in generated_sql:
                        generated_sql = generated_sql.replace("WHERE", "WHERE LOWER(")
                        if "=" in generated_sql:
                            parts = generated_sql.split("=", 1)
                            generated_sql = f"{parts[0]}) ={parts[1]}"
                
                new_experiment['results']['test_results'].append({
                    "nl": test_item['nl'],
                    "expected_sql": test_item['sql'],
                    "generated_sql": generated_sql,
                    "is_correct": is_correct
                })
            
            # Add to session state
            st.session_state.experiments.append(new_experiment)
            st.session_state.current_experiment = new_experiment
            
            # Navigate to list tab to see results
            st.session_state.experiment_tab = "list"
            st.success(f"Experiment '{exp_name}' created and executed successfully!")
            st.rerun()

# 함수 정의
def navigate_to_assistant_page():
    st.session_state.navigate_to_assistant = True

# Implement experiment list tab
with tab_list:
    st.header("Experiment List")
    
    # 필터링을 위한 test set 목록 생성
    all_test_sets = ["All Test Sets"]
    test_set_dict = {}
    
    # 워크스페이스 실험 목록
    workspace_experiments = [e for e in st.session_state.experiments 
                          if e['workspace_id'] == st.session_state.current_workspace['id']]
    
    # Test Set 목록 생성
    for e in workspace_experiments:
        if 'material' in e and 'test_set_name' in e['material']:
            test_set_name = e['material'].get('test_set_name', 'Unknown')
            if test_set_name not in all_test_sets:
                all_test_sets.append(test_set_name)
                test_set_dict[test_set_name] = []
            
            # 해당 Test Set에 실험 추가
            if test_set_name in test_set_dict:
                test_set_dict[test_set_name].append(e)
    
    # Test set 선택 필터 추가
    selected_test_set = st.selectbox("Filter by Test Set", all_test_sets)
    
    # 선택된 test set에 따라 필터링
    if selected_test_set != "All Test Sets":
        filtered_experiments = [e for e in workspace_experiments 
                             if e.get('material', {}).get('test_set_name', '') == selected_test_set]
    else:
        filtered_experiments = workspace_experiments
    
    if not filtered_experiments:
        st.info("No experiments created yet in this workspace. Create one in the 'Create' tab.")
    else:
        # Create a dataframe for experiments
        exp_data = []
        for exp in filtered_experiments:
            # material 정보에 train_set_name과 test_set_name 포함
            train_set_name = exp['material'].get('train_set_name', 'Unknown')
            test_set_name = exp['material'].get('test_set_name', 'Unknown')
            
            exp_data.append({
                "ID": exp['id'],
                "Name": exp['name'],
                "Dataset": f"{exp['dataset']['project']}.{exp['dataset']['dataset']}",
                "Material": exp['material']['name'],
                "Train Set": train_set_name,  # 새로 추가
                "Test Set": test_set_name,    # 새로 추가
                "Accuracy": f"{exp['results']['accuracy'] * 100:.1f}%",
                "Created": exp['created_at'],
                "Status": exp['status']
            })
        
        exp_df = pd.DataFrame(exp_data)
        st.dataframe(
            exp_df,
            column_config={
                "ID": None,  # Hide ID column
                "Name": "Experiment Name",
                "Train Set": "Training Set",  # 새로 추가
                "Test Set": "Test Set",       # 새로 추가
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["completed", "failed", "running"],
                    width="small"
                ),
                "Accuracy": st.column_config.ProgressColumn(
                    "Accuracy",
                    min_value=0,
                    max_value=100,
                    format="%f%%",
                ),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # 동일 Test Set에 대한 정확도 비교 그래프
        if filtered_experiments and selected_test_set != "All Test Sets":
            st.subheader(f"Accuracy Comparison for Test Set: {selected_test_set}")
            
            # 그래프 데이터 준비
            chart_data = []
            for exp in filtered_experiments:
                # 날짜 파싱
                created_at = datetime.datetime.strptime(exp['created_at'], "%Y-%m-%d %H:%M:%S")
                
                chart_data.append({
                    "experiment": exp['name'],
                    "accuracy": exp['results']['accuracy'] * 100,  # 백분율로 변환
                    "date": created_at
                })
            
            # 날짜순으로 정렬
            chart_data = sorted(chart_data, key=lambda x: x['date'])
            
            # 데이터프레임 생성
            chart_df = pd.DataFrame(chart_data)
            
            # line plot 생성
            if not chart_df.empty:
                fig = px.line(
                    chart_df, 
                    x="experiment", 
                    y="accuracy", 
                    markers=True,
                    title=f"Accuracy Trend for Test Set: {selected_test_set}",
                    labels={"experiment": "Experiment", "accuracy": "Accuracy (%)"}
                )
                fig.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data to generate the chart.")
        
        # View details of selected experiment
        selected_exp_name = st.selectbox("Select experiment for details", 
                                      ["Select an experiment"] + [exp["name"] for exp in filtered_experiments])
        
        if selected_exp_name != "Select an experiment":
            # Find the selected experiment
            for exp in filtered_experiments:
                if exp["name"] == selected_exp_name:
                    selected_exp = exp
                    break
            
            # Display experiment details
            st.subheader(f"Experiment: {selected_exp['name']}")
            
            # Display dataset and material info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Dataset:** {selected_exp['dataset']['project']}.{selected_exp['dataset']['dataset']}")
                st.markdown(f"**Created:** {selected_exp['created_at']}")
            with col2:
                st.markdown(f"**Material:** {selected_exp['material']['name']}")
                train_set_name = selected_exp['material'].get('train_set_name', 'Unknown')
                st.markdown(f"**Train Set:** {train_set_name}")
            with col3:
                st.markdown(f"**Status:** {selected_exp['status']}")
                test_set_name = selected_exp['material'].get('test_set_name', 'Unknown')
                st.markdown(f"**Test Set:** {test_set_name}")
            
            # Knowledge data display (추가)
            if 'knowledge_data' in selected_exp['material'] and selected_exp['material']['knowledge_data']:
                with st.expander("Knowledge Data"):
                    st.write(selected_exp['material']['knowledge_data'])
            
            # Experiment results summary
            st.subheader("Results Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Accuracy", f"{selected_exp['results']['accuracy'] * 100:.1f}%")
            
            with col2:
                correct_count = sum(1 for r in selected_exp['results']['test_results'] if r['is_correct'])
                total_count = len(selected_exp['results']['test_results'])
                st.metric("Correct Queries", f"{correct_count}/{total_count}")
            
            with col3:
                error_rate = (total_count - correct_count) / total_count * 100 if total_count > 0 else 0
                st.metric("Error Rate", f"{error_rate:.1f}%")
            
            # Test results tab
            st.subheader("Test Results")
            
            # Create dataframe for test results
            test_results = []
            for idx, res in enumerate(selected_exp['results']['test_results']):
                test_results.append({
                    "idx": idx,
                    "Query": res['nl'],
                    "Generated SQL": res['generated_sql'][:50] + "...",
                    "Correct": "✅" if res['is_correct'] else "❌"
                })
            
            test_df = pd.DataFrame(test_results)
            # Display test results table without selection feature
            st.dataframe(
                test_df,
                column_config={
                    "idx": None,  # Hide index column
                    "Query": st.column_config.TextColumn("Natural Language Query"),
                    "Generated SQL": st.column_config.TextColumn("Generated SQL"),
                    "Correct": "Status"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Let user select a row for detailed view
            selected_idx = st.selectbox(
                "Select a query to see detailed comparison:",
                options=test_df["idx"].tolist(),
                format_func=lambda x: f"{test_df[test_df['idx']==x]['Query'].iloc[0][:50]}..."
            )
            
            # Show detail of selected test result
            if selected_idx is not None:
                result = selected_exp['results']['test_results'][selected_idx]
                
                st.subheader("Detailed Comparison")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Expected SQL**")
                    st.code(result['expected_sql'], language="sql")
                
                with col2:
                    st.markdown("**Generated SQL**")
                    st.code(result['generated_sql'], language="sql")
                
                # For demo, we'll just highlight some differences manually
                if not result['is_correct']:
                    st.error("Differences detected!")
                    
                    # 차이점 강조 표시
                    st.subheader("SQL Differences")
                    
                    # 간단한 차이점 표시 - WHERE 절 변경을 찾아서 표시
                    if "WHERE" in result['expected_sql'] and "WHERE" in result['generated_sql']:
                        expected_where = result['expected_sql'].split("WHERE")[1].strip().split()[0]
                        generated_where = result['generated_sql'].split("WHERE")[1].strip().split()[0]
                        
                        if expected_where != generated_where:
                            st.markdown(f"**WHERE clause modified:**")
                            st.markdown(f"- Expected: `WHERE {expected_where}`")
                            st.markdown(f"- Generated: `WHERE {generated_where}`")
                    
                    # 일반적인 힌트 제공
                    st.info("Hint: Check the WHERE clause conditions, function calls, and column references.")
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Deploy as Assistant", use_container_width=True):
                    # Create a new assistant
                    new_assistant = {
                        "id": str(uuid.uuid4()),
                        "name": f"Assistant from {selected_exp['name']}",
                        "description": f"Created from experiment {selected_exp['name']}",
                        "workspace_id": st.session_state.current_workspace['id'],
                        "experiment_id": selected_exp['id'],
                        "dataset": selected_exp['dataset'],
                        "material": selected_exp['material'],
                        "version": 1,
                        "status": "active",
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Add to session state
                    st.session_state.assistants.append(new_assistant)
                    st.session_state.current_assistant = new_assistant
                    st.session_state.current_assistant_version = 1
                    
                    st.success(f"Assistant created from experiment '{selected_exp['name']}'!")
                    
                    # 버튼 클릭 핸들러 설정
                    if st.button("Go to Assistants Page", on_click=navigate_to_assistant_page):
                        pass  # 버튼이 클릭되면 on_click 함수가 호출됩니다
            
            with col2:
                if st.button("Retry Experiment", use_container_width=True):
                    # Set up for a new experiment with the same data
                    st.session_state.selected_dataset = selected_exp['dataset']
                    st.session_state.selected_material = selected_exp['material']
                    # Switch to create tab
                    st.session_state.experiment_tab = "create"
                    st.rerun()

# 페이지 전환 확인 (코드 끝부분에 추가)
if st.session_state.navigate_to_assistant:
    st.session_state.navigate_to_assistant = False  # 상태 재설정
    st.switch_page("pages/03_assistant.py")