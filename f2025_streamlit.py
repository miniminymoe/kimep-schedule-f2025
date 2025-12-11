import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re

# Page configuration
st.set_page_config(page_title="KIMEP F2025 Dashboard", layout="wide", page_icon="https://cdn.brandfetch.io/idg3xG-Bto/w/500/h/500/theme/dark/icon.jpeg?c=1dxbfHSJFAPEGdCLU4o5B")

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Read file
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    
    # Data type conversion
    for col in ['Code', 'Sec.', 'Days', 'Days1', 'Days2', 'Days3', 'Days4', 'Days5', 'College', 'Instructor', 'Hall', 'Type']:
        if col in df.columns:
            df[col] = df[col].astype(str).replace('nan', np.nan)
    
    for col in ['Reg. Stud.', 'Limit', 'Hall capacity', 'Duration', 'TotalDuration', 'KIMEP Credit', 'ECTS Credit', 'Late Registration']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

# File upload (only show if data not loaded)
if not st.session_state.data_loaded:
    st.title("🎓 KIMEP F2025 Dashboard")
    uploaded_file = st.file_uploader("Upload F2025 Schedule Excel File (xlsx)", type=['xlsx'])
    
    if uploaded_file is None:
        st.stop()
    else:
        df = load_data(uploaded_file)
        st.session_state.df = df
        st.session_state.data_loaded = True
        st.rerun()
else:
    df = st.session_state.df

# Navigation
st.title("🎓 KIMEP F2025 Dashboard")
tab1, tab2, tab3 = st.tabs([
    "📚 Academic Operations & Performance",
    "👨‍🏫 Faculty Activity & Resource Utilization", 
    "🏛️ Facilities & Space Optimization"
])



# ==================== TAB 1: Academic Operations & Performance ====================
with tab1:
    st.header("📚 Academic Operations & Performance")
    st.markdown("Understanding Student Demand and Enrollment Patterns")
    st.divider()
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)

    # --- 고유한 Index를 기준으로 학위별 과정 수를 계산하기 위한 전처리 (수정됨) ---
    
    # 1. Code에서 가장 처음 나오는 숫자를 추출하는 함수 (정규 표현식 사용)
    def extract_first_digit(code):
        if pd.isna(code):
            return None
        # 문자열에서 첫 번째로 0-9에 해당하는 숫자를 찾습니다.
        match = re.search(r'\d', str(code))
        return int(match.group(0)) if match else None
    
    df['First_Digit'] = df['Code'].apply(extract_first_digit)
    
    # 2. Index가 동일한 row는 하나로 세기 위해, Index만을 기준으로 고유한 행을 찾습니다.
    #    *** 사용자 요청에 따라 'Index' 컬럼만 사용하여 중복을 방지합니다. ***
    df_unique_by_index = df.drop_duplicates(subset=['Index'])
    
    # 3. First_Digit이 유효하게 추출된 강좌만 최종 집계 대상(df_unique)으로 선정합니다.
    df_unique = df_unique_by_index[df_unique_by_index['First_Digit'].notna()]
    
    # --- col1: Total Courses (고유한 Index를 기준으로 계산) ---
    with col1:
        # col2~col4의 기반이 되는, Index 중복이 제거된 유효 강좌의 개수를 사용합니다.
        total_courses_count = df_unique.shape[0] 
        st.metric("Total Courses", f"{total_courses_count:,}")
    
    # --- col2: Number of Undergraduate Courses (Code의 첫 번째 숫자 1, 2, 3, 4) ---
    with col2:
        # df_unique를 사용하여 Index 중복 방지
        undergrad_count_new = df_unique[df_unique['First_Digit'].isin([1, 2, 3, 4])].shape[0]
        st.metric("Undergraduate Courses", f"{undergrad_count_new:,}")
    
    # --- col3: Number of Graduate Courses (Code의 첫 번째 숫자 5, 6, 7, 8, 9) ---
    with col3:
        # df_unique를 사용하여 Index 중복 방지
        masters_digits = [5, 6, 7, 8, 9] 
        master_count = df_unique[df_unique['First_Digit'].isin(masters_digits)].shape[0]
        st.metric("Graduate Courses", f"{master_count:,}")
    
    # --- col4: Number of Foundation Courses (Code의 첫 번째 숫자 0) ---
    with col4:
        # df_unique를 사용하여 Index 중복 방지
        foundation_count = df_unique[df_unique['First_Digit'] == 0].shape[0]
        st.metric("Foundation Courses", f"{foundation_count:,}")

    
    st.divider()
    
# College filter
    if 'College' in df.columns:
        

        # --- Checkbox Color Override ---
        st.markdown("""
        <style>

            /* 체크박스 외곽선(테두리) 색 */
            div[data-testid="stCheckbox"] svg {
                stroke: #5A448F !important;
            }

            /* 체크된 상태: 배경은 보라색, 체크 마크는 흰색 */
            div[data-testid="stCheckbox"] svg[data-checked="true"] path {
                fill: #5A448F !important;
                stroke: white !important;
            }

        </style>
        """, unsafe_allow_html=True)


        
        # ... (나머지 코드는 이전과 동일합니다.)        
        # 1. 사용자 정의 정렬 순서 정의 및 고유 College 목록 생성 (이전과 동일)
        custom_order = ['BCB', 'CSS', 'CHSE', 'LAW', 'SCSM', 'GEN', 'SPORT', 'FOUNDATION']
        # ... (이하 코드는 이전과 완전히 동일합니다.)
        
        unique_colleges = df['College'].dropna().unique().tolist()
        
        ordered_colleges = [
            college for college in custom_order if college in unique_colleges
        ]
        remaining_colleges = [
            college for college in unique_colleges if college not in custom_order
        ]
        
        # 최종 정렬된 College 목록
        options_for_checkbox = ordered_colleges + sorted(remaining_colleges)
        
        # 2. 체크박스 위젯들을 담을 컨테이너 생성 및 선택 목록 초기화
        st.markdown("##### Select College(s)")
        
        selected_colleges_list = []
        
        # 체크박스를 가로로 나열하기 위해 Column을 사용합니다.
        cols = st.columns(min(len(options_for_checkbox), 4)) 
        
        # 3. 각 College마다 체크박스를 생성하고 상태를 확인합니다.
        for i, college in enumerate(options_for_checkbox):
            col_index = i % len(cols) 
            
            with cols[col_index]:
                # 기본적으로 모든 College가 선택된 상태(True)로 시작합니다.
                if st.checkbox(college, value=True, key=f'check_{college}'):
                    selected_colleges_list.append(college)
        
        # 4. 필터링 로직: 체크된 대학 목록(selected_colleges_list)에 포함되는 row만 필터링합니다.
        if selected_colleges_list: 
            filtered_df = df[df['College'].isin(selected_colleges_list)].copy()
        else:
            st.warning("⚠️ Please select at least one College.")
            filtered_df = df.iloc[0:0] 
    
    else:
        filtered_df = df.copy()
    
    st.divider()

        # 1. Enrollment Profile
    st.subheader("Enrollment Profile")


    row1_col1, row1_col2 = st.columns([4.5, 5.5])

    
    
    with row1_col1:
            st.markdown("**Enrolled Students per College**")
            if 'College' in df.columns and 'Reg. Stud.' in df.columns:
                college_enroll = filtered_df.groupby('College')['Reg. Stud.'].sum().reset_index()
                college_enroll = college_enroll.sort_values('Reg. Stud.', ascending=False)
                college_enroll['Percentage'] = (college_enroll['Reg. Stud.'] / college_enroll['Reg. Stud.'].sum() * 100).round(1)
                
                fig = px.bar(college_enroll, x='College', y='Reg. Stud.',
                             labels={'Reg. Stud.': 'Students', 'College': 'College'},
                             color='Reg. Stud.',
                             color_continuous_scale='Blues',
                             text='Percentage',
                             hover_data={'Reg. Stud.': ':,', 'Percentage': ':.1f'})
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                
                # 🚨 수정된 부분: height를 350에서 500으로 증가
                fig.update_layout(showlegend=False, height=500) 
                
                st.plotly_chart(fig, use_container_width=True)
            
    with row1_col2:
            st.markdown("**Top 10 General Education Courses**")
            if 'College' in df.columns and 'Reg. Stud.' in df.columns and 'Title' in df.columns:
                gen_courses = filtered_df[filtered_df['College'].str.lower() == 'gen'].copy()
                if len(gen_courses) > 0:
                    gen_top = gen_courses.groupby(['Code', 'Title'])['Reg. Stud.'].sum().reset_index()
                    gen_top = gen_top.sort_values('Reg. Stud.', ascending=False).head(10)
                    
                    # 🚨 수정된 부분: Code를 제거하고 Title만 사용하여 Course 레이블 생성
                    gen_top['Course'] = gen_top['Title'].str[:40] # 제목이 길 경우를 대비해 40자까지 자름
                    
                    fig = px.bar(gen_top, x='Reg. Stud.', y='Course',
                                 orientation='h',
                                 color='Reg. Stud.',
                                 color_continuous_scale='Greens',
                                 text='Reg. Stud.')
                    
                    # 🚨 수정된 부분: texttemplate에 ' Students' 문자열 추가
                    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                    
                    # 🚨 레이블 수정 위치: update_layout에 xaxis_title과 yaxis_title 추가
                    fig.update_layout(
                        showlegend=False, 
                        height=500, 
                        yaxis={'categoryorder':'total ascending'},
                        # --- X축과 Y축 레이블 설정 ---
                        xaxis_title="Enrolled Students",
                        yaxis_title="Course Titles" 
                        # ---------------------------
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No general education courses found")

                
    st.divider()
    
    
# 3. Course Distribution by Day
    # 🚨 원래 st.subheader("Course Distribution")와 st.markdown("**Classes and Students by Day**") 복구

    days_columns = [col for col in df.columns if col in ['Days1', 'Days2', 'Days3', 'Days4', 'Days5']]
    
    # 🚨 'day_data' 초기화는 이전에 이 블록 내부에서 진행되었으므로, 구조를 유지합니다.
    if days_columns and 'Reg. Stud.' in df.columns:
        # Create a dataset with all day occurrences
        day_data = [] # <--- 이 부분이 반드시 정의되어야 합니다.
        for idx, row in filtered_df.iterrows():
            days_in_row = []
            for col in days_columns:
                if pd.notna(row[col]):
                    days_in_row.append(row[col])
            
            for day in days_in_row:
                day_data.append({
                    'Day': day,
                    'Students': row['Reg. Stud.'] if pd.notna(row['Reg. Stud.']) else 0
                })
        
        # 🚨 if day_data: 조건문 안에서 나머지 로직 실행
        if day_data:
            day_df = pd.DataFrame(day_data)
            
            # Aggregate
            day_summary = day_df.groupby('Day').agg({
                'Students': ['count', 'sum']
            }).reset_index()
            day_summary.columns = ['Day', 'Classes', 'Total Students']
            
            # Sort by day order
            day_order = ['M', 'T', 'W', 'Th', 'F']
            day_summary['Day'] = pd.Categorical(day_summary['Day'], categories=day_order, ordered=True)
            day_summary = day_summary.sort_values('Day')

            st.subheader("Course Distribution")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Classes by Day Chart (꺾은선형 차트, 색상 및 여백 적용)
                fig = px.line(day_summary, x='Day', y='Classes',
                              text='Classes',
                              labels={'Classes': 'Number of Classes', 'Day': 'Day of the Week'}) 
                
                fig.update_traces(mode='lines+markers+text', 
                                  line_color='darkblue', 
                                  marker=dict(color='deepskyblue', size=8),
                                  texttemplate='%{text}', textposition='top center')
                
                # 🚨 수정된 부분: height를 500으로 복구하고, yaxis range를 [100, 400]으로 설정
                fig.update_layout(showlegend=False, height=400, 
                                  title='Number of Classes by Day',
                                  margin=dict(b=50), # 텍스트 잘림 방지용으로 t=180 재적용
                                  yaxis=dict(range=[150, 400]) 
                                 ) 
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Students by Day Chart (꺾은선형 차트, 색상 및 여백 적용)
                fig = px.line(day_summary, x='Day', y='Total Students',
                              text='Total Students',
                              labels={'Total Students': 'Total Enrolled Students', 'Day': 'Day of the Week'})
                
                fig.update_traces(mode='lines+markers+text', 
                                  line_color='darkorange', 
                                  marker=dict(color='gold', size=8),
                                  texttemplate='%{text:,}', textposition='top center')
                
                # 🚨 수정된 부분: height를 500으로 복구하고, yaxis range를 [3000, 7000]으로 설정
                fig.update_layout(showlegend=False, height=400, 
                                  title='Total Students by Day',
                                  margin=dict(b=50), # 텍스트 잘림 방지용으로 t=180 재적용
                                  yaxis=dict(range=[2500, 7000])
                                 )
                st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("No day distribution data available")        


    st.divider()
    
# 4. Time Distribution
    st.subheader("Peak Time Analysis")
    
    # 🚨 수정된 부분: Credit Type 필터를 두 차트 위에 공통으로 배치
    if 'KIMEP Credit' in filtered_df.columns:
        credit_filter = st.radio("Select KIMEP Credit Type", 
                                 ['All', '2 Credits', '3 Credits'], 
                                 horizontal=True, key='global_credit_filter')
    else:
        credit_filter = 'All'
        
    # 두 차트 데이터를 모두 필터링하기 위해 'filtered_df'에 학점 필터를 적용하는 임시 데이터프레임 생성
    temp_df = filtered_df.copy()
    if credit_filter == '2 Credits':
        temp_df = temp_df[temp_df['KIMEP Credit'] == 2]
    elif credit_filter == '3 Credits':
        temp_df = temp_df[temp_df['KIMEP Credit'] == 3]


    # 4번과 5번을 양 옆으로 배치하기 위해 새로운 컬럼 정의
    time_col, duration_col = st.columns(2) 
    
    
    # === 4. Time Distribution (왼쪽 컬럼) ===
    with time_col:
        st.markdown("**Classes by Start Hour**")

        if 'Time' in temp_df.columns:
            # 🚨 수정: 필터링된 temp_df 사용
            df_time = temp_df.copy() 
            df_time['Start_Time'] = df_time['Time'].str.split('-').str[0].str.strip()
            df_time['Start_Hour'] = df_time['Start_Time'].str.split(':').str[0]
            df_time['Start_Hour'] = pd.to_numeric(df_time['Start_Hour'], errors='coerce')
            
            # Filter valid hours (8:30 to 20:30)
            df_time = df_time[(df_time['Start_Hour'] >= 8) & (df_time['Start_Hour'] <= 20)]
            
            # ... (나머지 time_dist 차트 로직 유지) ...
            
            time_dist = df_time.groupby('Start_Hour').size().reset_index(name='Classes')
            time_dist = time_dist.sort_values('Start_Hour')
            time_dist['Start_Hour'] = time_dist['Start_Hour'].astype(str) + ':00' 
            
            fig = px.line(time_dist, x='Start_Hour', y='Classes',
                         text='Classes',
                         labels={'Start_Hour': 'Start Hour', 'Classes': 'Numbers of Classes'})
            
            fig.update_traces(mode='lines+markers+text', 
                              line_color='purple', 
                              marker=dict(color='plum', size=8),
                              texttemplate='%{text}', 
                              textposition='top center')
            
            fig.update_layout(showlegend=False, height=500)
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Time column is missing in the data.")
    
    # === 5. Duration Distribution (오른쪽 컬럼) ===
    with duration_col:
        st.markdown("**Distribution by Class Length**")

        # Duration과 Type 컬럼 모두 있는지 확인
        if 'Duration' in temp_df.columns and 'Type' in temp_df.columns: 
            df_duration = temp_df.copy()
            
            # 🚨 수정된 부분: TotalDuration 대신 'Type' 컬럼을 사용하여 back-to-back 식별
            df_duration['Is_BackToBack'] = df_duration['Type'].astype(str).str.contains('back', case=False, na=False)
            
            # Mark all sections of back-to-back classes
            back_to_back_codes = df_duration[df_duration['Is_BackToBack']]['Code'].unique()
            df_duration['Skip'] = False
            
            for code in back_to_back_codes:
                code_rows = df_duration[df_duration['Code'] == code]
                if len(code_rows) > 1:
                    # Keep only first occurrence, mark others to skip
                    indices = code_rows.index[1:]
                    df_duration.loc[indices, 'Skip'] = True
            
            df_duration = df_duration[~df_duration['Skip']]
            
            # Assign effective duration (Is_BackToBack이 True면 150분, 아니면 Duration 값)
            df_duration['Effective_Duration'] = df_duration.apply(
                lambda row: 150 if row['Is_BackToBack'] else row['Duration'],
                axis=1
            )
            
            # 50분, 75분, 150분(back-to-back)만 포함하도록 필터링
            df_duration = df_duration[df_duration['Effective_Duration'].isin([50, 75, 150])]

            if len(df_duration) > 0:
                duration_counts = df_duration['Effective_Duration'].value_counts().reset_index()
                duration_counts.columns = ['Duration (min)', 'Count']
                
                # 백분율 계산
                total_classes = duration_counts['Count'].sum()
                duration_counts['Percentage'] = (duration_counts['Count'] / total_classes) * 100
                
                duration_counts = duration_counts.sort_values('Duration (min)')
                duration_counts['Duration (min)'] = duration_counts['Duration (min)'].astype(str) + ' min'
                
                # 파란색 계열 차트 생성
                fig = px.bar(duration_counts, x='Duration (min)', y='Percentage',
                             color='Percentage',
                             color_continuous_scale='Blues', 
                             text='Percentage',
                             labels={'Percentage': 'Percentage (%)'}) 
                             
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                
                fig.update_layout(showlegend=False, height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No 50, 75, or 150 minute class data available for {credit_filter}")
        else:
            st.info("Required columns (Duration or Type) are missing in the data.")
            
            
    st.divider()
    
    st.subheader("Course Registration Pattern Analysis")
    st.markdown("**Top 10 Courses with the Highest Number of Late Registrations**")
    
    if 'Late Registration' in df.columns and 'Code' in df.columns and 'Title' in df.columns:
        late_reg = filtered_df.groupby(['Code', 'Title'])['Late Registration'].sum().reset_index()
        late_reg = late_reg.sort_values('Late Registration', ascending=False).head(10)
        
        # 🚨 수정된 부분: Code를 제거하고 Title만 사용하여 Course 레이블 생성
        late_reg['Course'] = late_reg['Title'].str[:40] # 제목이 길 경우를 대비해 40자까지 자름
        
        if len(late_reg) > 0:
            fig = px.bar(late_reg, x='Late Registration', y='Course',
                         orientation='h',
                         color='Late Registration',
                         color_continuous_scale='Reds',
                         text='Late Registration')
            
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            
            fig.update_layout(showlegend=False, 
                              height=400, 
                              yaxis={'categoryorder':'total ascending'})
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No late registration data available")


            
# ==================== TAB 2: Faculty Activity & Resource Utilization ====================
with tab2:
    st.header("👨‍🏫 Faculty Activity & Resource Utilization")
    st.markdown("Monitoring Faculty Workload and Teaching Allocation")
    st.divider()
    # *************************************************************
    # 1. Key Metrics Placeholder (필터보다 먼저 위치)
    # *************************************************************
    # 🚨 수정: Key Metrics가 들어갈 자리를 먼저 잡아둡니다.
    metrics_placeholder = st.empty()
    st.divider()

    # *************************************************************
    # 2. 통합 필터 섹션: Select Filters
    # *************************************************************
    
    st.markdown("#### Select Filters")

    # --- College 필터 ---
    if 'College' in df.columns:
        # (CSS는 생략)
        
        custom_order = ['BCB', 'CSS', 'CHSE', 'LAW', 'SCSM', 'GEN', 'SPORT', 'FOUNDATION']
        unique_colleges = df['College'].dropna().unique().tolist()
        ordered_colleges = [c for c in custom_order if c in unique_colleges]
        remaining_colleges = [c for c in unique_colleges if c not in custom_order]
        options_for_checkbox = ordered_colleges + sorted(remaining_colleges)
        
        selected_colleges_list = []
        
        st.markdown("##### 1. Select College(s)")
        
        cols = st.columns(min(len(options_for_checkbox), 5))  
        
        for i, college in enumerate(options_for_checkbox):
            col_index = i % len(cols)  
            
            with cols[col_index]:
                if st.checkbox(college, value=True, key=f'tab2_check_college_filter_unique_{college}'): 
                    selected_colleges_list.append(college)
        
        # 4. 필터링 로직 (1단계): College 필터 적용
        if selected_colleges_list:  
            filtered_df = df[df['College'].isin(selected_colleges_list)].copy()
        else:
            st.warning("⚠️ Please select at least one College.")
            filtered_df = df.iloc[0:0]  
    
    else:
        filtered_df = df.copy()

    
    # --- Empty-Time Classes 필터 ---
    st.markdown("##### 2. Select Courses")
    
    include_special = st.checkbox(
        "Include Empty-Time Classes (00:00 - 00:00)", 
        value=True, 
        key='tab2_empty_time_course_filter_unique' 
    )

    # 5. 필터링 로직 (2단계): Empty-Time Classes 필터 적용
    
    if not filtered_df.empty and 'Time' in filtered_df.columns:
        
        if not include_special:
            # 🚨 수정: 'Time'이 '00:00 - 00:00'인 행을 정확히 제외
            filtered_df = filtered_df[filtered_df['Time'] != '00:00 - 00:00'].copy() 
            
    # *************************************************************
    # 3. Key Metrics (Placeholder에 최종 filtered_df를 사용하여 결과 그리기)
    # *************************************************************
    
    with metrics_placeholder.container(): # 이전에 잡아둔 위치에 메트릭을 그립니다.
        col1, col2, col3 = st.columns(3)
        
        if not filtered_df.empty and 'Instructor' in filtered_df.columns:
            total_instructors = filtered_df['Instructor'].nunique()
            
            # col1: Total Instructors
            with col1:
                st.metric("Total Instructors", total_instructors) 

            # col2: Avg Courses/Instructor 
            with col2:
                if 'Index' in filtered_df.columns:
                    total_courses = filtered_df['Index'].nunique()
                    
                    if total_instructors > 0:
                        avg_courses = total_courses / total_instructors
                        st.metric("Avg Courses per Instructor", f"{avg_courses:.1f}")
                    else:
                        st.metric("Avg Courses per Instructor", "N/A (No Instructors)")
                else:
                    st.metric("Avg Courses per Instructor", "N/A (Index Missing)")


            # col3: Avg Students per Instructor
            with col3:
                if 'Reg. Stud.' in filtered_df.columns:
                    total_students_per_instructor = filtered_df.groupby('Instructor')['Reg. Stud.'].sum()
                    
                    if not total_students_per_instructor.empty:
                        avg_students_per_instructor = total_students_per_instructor.mean()
                        st.metric("Avg Students per Instructor", f"{avg_students_per_instructor:.0f}")
                    else:
                        st.metric("Avg Students per Instructor", "0")
                else:
                    st.metric("Avg Students per Instructor", "N/A (Data Missing)")
        else:
            with col1:
                st.info("No data available for Key Metrics after filtering.")

    st.divider() # Key Metrics와 Teaching Load Analysis 사이에 구분선 추가



    # *************************************************************
    # 6. College Summary (단과대별 교수 인원 현황)
    # *************************************************************
    st.subheader("🏛️ College Summary")
    
    if 'College' in filtered_df.columns and 'Instructor' in filtered_df.columns:
        
        # 로직: College별 고유한 Instructor 수 계산
        college_instructor_count = filtered_df.groupby('College')['Instructor'].nunique().reset_index()
        college_instructor_count.columns = ['College', 'Unique Instructors']
        
        # 🚨 수정: 차트 유형을 도넛 차트(Pie with hole)로 변경
        fig = px.pie(college_instructor_count, 
                     values='Unique Instructors',
                     names='College', # 단과대 이름을 레이블로 사용
                     hole=.4, # 도넛 차트로 만들기 위해 hole 설정
                     color='College', # 개별 색상 적용
                     title="Percentage of Instructors by Department")
        
        # 백분율을 차트 위에 표시
        fig.update_traces(textinfo='percent+label', 
                          pull=[0.05] * len(college_instructor_count), # 시각적 강조를 위해 약간의 간격 설정
                          textposition='outside')
        
        fig.update_layout(height=500)
        
        st.plotly_chart(fig, use_container_width=True, key='tab2_chart_college_instructor_count')
        
        
    else:
        st.info("College or Instructor column is missing in the data.")


    st.divider() 
        
    # *************************************************************
    # 4. Teaching Load Analysis (필터링된 filtered_df 사용)
    # *************************************************************

    st.subheader("📚 Teaching Load Analysis")
    
    row1_col1, row1_col2 = st.columns([4.5,5.5])
    
    if not filtered_df.empty: 
        
        with row1_col1:
            st.markdown("**Courses per Instructor**")
            if 'Instructor' in filtered_df.columns and 'Index' in filtered_df.columns: 
                
                instructor_load = filtered_df.groupby('Instructor')['Index'].nunique().reset_index(name='Courses')
                
                instructor_load = instructor_load.sort_values('Courses', ascending=False).head(15)
                
                instructor_load = instructor_load[instructor_load['Instructor'].notna()]
                
                if not instructor_load.empty:
                    fig = px.bar(instructor_load, x='Courses', y='Instructor',
                                  orientation='h',
                                  color='Courses',
                                  color_continuous_scale='Blues',
                                  text='Courses')
                    fig.update_traces(texttemplate='%{text}', textposition='outside')
                    fig.update_layout(showlegend=False, height=450, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Instructor data is not available or empty after cleaning.")
            else:
                st.warning("⚠️ Dataframe requires 'Instructor' and 'Index' columns for this chart.")

                
        with row1_col2:
            st.markdown("**Total Students per Instructor**")
            if 'Instructor' in filtered_df.columns and 'Reg. Stud.' in filtered_df.columns:
                instructor_students = filtered_df.groupby('Instructor')['Reg. Stud.'].sum().reset_index()
                instructor_students = instructor_students.sort_values('Reg. Stud.', ascending=False).head(15)
                
                if not instructor_students.empty:
                    fig = px.bar(instructor_students, x='Reg. Stud.', y='Instructor',
                                  orientation='h',
                                  color='Reg. Stud.',
                                  color_continuous_scale='Oranges',
                                  text='Reg. Stud.')
                    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                    fig.update_layout(showlegend=False, height=450, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No student data available for instructors after filtering.")
            else:
                st.warning("⚠️ Dataframe requires 'Instructor' and 'Reg. Stud.' columns for this chart.")
    else:
        st.info("No data available for Teaching Load Analysis after filtering.")
    
    
    




# ==================== TAB 3: Facilities & Space Optimization ====================
with tab3:
    st.header("🏛️ Facilities & Space Optimization")
    st.markdown("Analyzing Classroom and Campus Space Usage")
    st.divider()



    col1, col2, col3 = st.columns(3)
    
    if 'Hall' in df.columns and 'Hall capacity' in df.columns:
        
        # 1. 데이터 클리닝 및 필터링
        capacity_df = df.copy()
        # Hall capacity를 숫자형으로 변환 (숫자가 아닌 값은 NaN으로 처리)
        capacity_df['Hall capacity'] = pd.to_numeric(capacity_df['Hall capacity'], errors='coerce')
        
        # 🚨 수정된 조건: Hall 유효성 검사 강화
        
        # Hall에 값이 있고 (notna()), Hall capacity가 숫자로 존재하며 (notna()), 
        # 🚨 Hall 값에 최소한 하나의 숫자(\d)가 포함된 행만 추출
        valid_capacity_df = capacity_df[
            capacity_df['Hall'].notna() & 
            capacity_df['Hall capacity'].notna() & 
            capacity_df['Hall'].astype(str).str.contains(r'\d', na=False) 
        ]
        
        if not valid_capacity_df.empty:
            
            # 1. Total Rooms
            with col1:
                # 유효한 강의실의 고유 개수
                total_rooms = valid_capacity_df['Hall'].nunique()
                st.metric("Total Rooms", total_rooms)
            
            # 2. Min Room capacity
            with col2:
                # 유효한 강의실의 수용 인원 최소값
                min_capacity = valid_capacity_df['Hall capacity'].min()
                st.metric("Min Room capacity", f"{min_capacity:.0f}")
            
            # 3. Max Room capacity
            with col3:
                # 유효한 강의실의 수용 인원 최대값
                max_capacity = valid_capacity_df['Hall capacity'].max()
                st.metric("Max Room capacity", f"{max_capacity:.0f}")
        else:
            with col1:
                st.info("No valid room data found for metrics after cleaning.")
    else:
        with col1:
            st.info("Required columns ('Hall' or 'Hall capacity') are missing.")
            
    st.divider()




    # *************************************************************
    # 7. Building Summary (수정됨: 파이 차트 및 영어 제목)
    # *************************************************************
    st.subheader("🏫 Building Summary") # 🚨 제목 영어로 변경
    
    if 'Hall' in df.columns:
        
        # 1. 빌딩 이름 추출 및 데이터 클리닝
        building_df = df.copy() 
        
        # 로직 1: Hall에서 슬래시(/) 뒤의 문자열 추출하여 Building 컬럼 생성
        building_df['Building'] = building_df['Hall'].astype(str).str.split('/').str[1].str.strip()
        
        # 2. 유효성 필터링
        valid_building_df = building_df[
            building_df['Hall'].notna() & 
            building_df['Building'].notna()
        ]
        
        # 3. 집계: Building별 고유한 Hall (강의실) 개수 계산
        building_room_count = valid_building_df.groupby('Building')['Hall'].nunique().reset_index()
        building_room_count.columns = ['Building', 'Total Rooms']
        
        if not building_room_count.empty:
            
            # 4. 🚨 수정: 파이 차트 (도넛 형태) 생성
            fig = px.pie(building_room_count, 
                         values='Total Rooms',
                         names='Building', # 빌딩 이름을 레이블로 사용
                         hole=.4, # 도넛 차트로 만들기 위해 hole 설정
                         color='Building', # 빌딩별 개별 색상 적용
                         title="Numbers of Rooms by Building") # 🚨 차트 제목 영어로 변경
            
            # 백분율과 레이블을 표시
            fig.update_traces(textinfo='percent+label', 
                              pull=[0.05] * len(building_room_count),
                              textposition='outside')
            
            fig.update_layout(height=500)
            
            st.plotly_chart(fig, use_container_width=True, key='tab2_chart_building_piechart') # 키 변경
            
        else:
            st.info("Building data could not be properly extracted from the 'Hall' column.")
            
    else:
        st.info("The 'Hall' column is missing from the data.")
    st.divider()
    
    # ... (나머지 Teaching Load Analysis, Distribution, Summary 코드는 그대로 유지) ...

    # 1. Room Utilization
    st.subheader("🏢 Room Utilization")
    
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
            st.markdown("**Top 10 Most Used Rooms by Classes**")
            
            if 'Hall' in df.columns and 'Index' in df.columns:
                
                # Hall별로 Unique한 Index 개수를 카운트 (Classes)
                room_usage = df.groupby('Hall')['Index'].nunique().reset_index(name='Classes')
                
                # Classes를 기준으로 내림차순 정렬 후 Top 10 추출
                room_usage = room_usage.sort_values('Classes', ascending=False).head(10)
                
                # 강의실 이름(Hall)에 값이 없는 행을 제외
                room_usage = room_usage[room_usage['Hall'].notna()]
                
                if not room_usage.empty:
                    fig = px.bar(room_usage, x='Classes', y='Hall',
                                  orientation='h',
                                  # Classes를 color 인자로 사용하여 연속적인 색상 스케일 적용
                                  color='Classes', 
                                  # 🚨 수정: 초록색 계열 팔레트 ('Greens') 적용
                                  color_continuous_scale='Greens',
                                  text='Classes')
                    
                    # 범례가 차트를 가릴 수 있으므로, 범례를 숨김
                    fig.update_traces(texttemplate='%{text}', textposition='outside')
                    fig.update_layout(showlegend=False, height=400, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True, key='tab2_chart_top_rooms')
                else:
                    st.info("No valid room usage data found after filtering.")
            else:
                st.warning("⚠️ Dataframe requires 'Hall' and 'Index' columns for this chart.")
            

            
    with row1_col2:
        st.markdown("**Distribution of Classes Used by Building**")
        
        if 'Hall' in df.columns and 'Index' in df.columns:
            
            # 1. 데이터 준비: Hall 컬럼 복사본을 만들어 문자열 처리
            class_df = df.copy() 
            
            # 로직: Hall에서 슬래시(/) 뒤의 문자열 추출하여 Building 컬럼 생성
            class_df['Building'] = class_df['Hall'].astype(str).str.split('/').str[1].str.strip()
            
            # 2. 유효성 필터링
            valid_class_df = class_df[
                class_df['Hall'].notna() & 
                class_df['Building'].notna() &
                class_df['Index'].notna()
            ]
            
            # 3. 집계: Building별 고유한 Index (수업) 개수 계산
            building_class_count = valid_class_df.groupby('Building')['Index'].nunique().reset_index()
            building_class_count.columns = ['Building', 'Total Classes']
            
            if not building_class_count.empty:
                
                # 4. 파이 차트 (도넛 형태) 생성
                fig = px.pie(building_class_count, 
                             values='Total Classes',
                             names='Building', 
                             hole=.4, # 도넛 차트
                             color='Building', )
                
                # 백분율과 레이블을 표시
                fig.update_traces(textinfo='percent+label', 
                                  pull=[0.05] * len(building_class_count),
                                  textposition='outside')
                
                fig.update_layout(height=400) # row1_col1의 높이와 맞춥니다.
                
                st.plotly_chart(fig, use_container_width=True, key='row1_col2_building_classes_piechart')
                
            else:
                st.info("No valid class data found after filtering.")
                
        else:
            st.warning("⚠️ Dataframe requires 'Hall' and 'Index' columns for this chart.")


            
    st.divider()
    
    st.subheader("Occupancy Rate Distribution")

    # 필수 컬럼이 있는지 확인합니다.
    if 'Reg. Stud.' in filtered_df.columns and 'Hall capacity' in filtered_df.columns and 'Index' in filtered_df.columns:
        
        # 1. filtered_df의 안전한 복사본을 만들어 Occupancy_Rate 계산
        df_for_occupancy = filtered_df.copy()
        
        # Hall capacity가 0인 경우를 처리하여 ZeroDivisionError 방지
        df_for_occupancy['Occupancy_Rate'] = (
            df_for_occupancy['Reg. Stud.'] / 
            df_for_occupancy['Hall capacity'].replace(0, pd.NA) * 100
        ).fillna(0).round(1)
        
        # 2. 데이터가 비어 있는지 최종 확인
        if not df_for_occupancy.empty:
            
            # 🚨 수정 1: 분석 텍스트를 st.subheader 바로 아래에 배치
            # 🚨 수정 2: 마크다운으로 텍스트를 왼쪽 정렬 (lefted)
            st.markdown(
                "**With classroom space underutilized in more than half of classes, most classroom assignments are oversized for current student demand, potentially leading to a waste of resources.**"
            )
            
            # 🚨 수정 3: 25% (여백), 50% (콘텐츠), 25% (여백) 비율로 컬럼을 나눕니다.
            # 50% 너비를 사용하도록 비율 [1, 2, 1] (총 4등분 중 2/4 = 50%)로 조정
            col_padding_left, col_content, col_padding_right = st.columns([1, 2, 1])
            
            with col_content: # 🚨 콘텐츠를 이 50% 너비의 컬럼 안에 배치합니다.
                
                # 히스토그램 생성 (df_for_occupancy 사용)
                fig = px.histogram(df_for_occupancy, x='Occupancy_Rate',
                                    nbins=20,
                                    labels={'Occupancy_Rate': 'Occupancy Rate (%)', 'count': 'Number of Classes'},
                                    color_discrete_sequence=['#636EFA'])
                fig.update_layout(showlegend=False, height=350)
                # use_container_width=True는 col_content의 50% 너비에 맞게 조정됩니다.
                st.plotly_chart(fig, use_container_width=True, key='occupancy_hist_final')
                
                # Stats (메트릭은 내부에서 3개의 서브 컬럼으로 분할)
                subcol1, subcol2, subcol3 = st.columns(3)
                
                # 50% 미만 (저활용)
                with subcol1:
                    under_50 = df_for_occupancy[df_for_occupancy['Occupancy_Rate'] < 50]['Index'].nunique()
                    st.metric("Under-utilized (<50%)", under_50)
                
                # 50%~90% 미만 (최적)
                with subcol2:
                    optimal = df_for_occupancy[(df_for_occupancy['Occupancy_Rate'] >= 50) & (df_for_occupancy['Occupancy_Rate'] < 90)]['Index'].nunique()
                    st.metric("Optimal (50-90%)", optimal)
                
                # 90% 이상 (과활용)
                with subcol3:
                    over_90 = df_for_occupancy[df_for_occupancy['Occupancy_Rate'] >= 90]['Index'].nunique()
                    st.metric("Over-utilized (≥90%)", over_90)
                
        else:
            st.info("No data available after applying filters.")
            
    else:
        st.warning("Required columns ('Reg. Stud.', 'Hall capacity', or 'Index') are missing for Occupancy Rate analysis.")

    # Download section
st.divider()
csv_data = df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 Download Full Data (CSV)",
    data=csv_data,
    file_name='university_schedule_data.csv',
    mime='text/csv',
)
