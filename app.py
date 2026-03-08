"""
Application: Carbon Registry AI Agent Training System
Runs offline with simulated data
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

from database_sim import db
from inquiry_analyzer import InquiryAnalyzer
from agent_tester import AgentTester

# Page configuration
st.set_page_config(
    page_title="Carbon Registry AI Agent Training",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_analyzer():
    return InquiryAnalyzer(db)

@st.cache_resource
def init_tester():
    return AgentTester(db, db.knowledge_base)

analyzer = init_analyzer()
tester = init_tester()

# Sidebar
with st.sidebar:
    st.title("🌲 Carbon Registry")
    st.markdown("### AI Agent Training System")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", 
         "🔍 Inquiry Analysis", 
         "🤖 Training Data Generator", 
         "🧪 Agent Testing", 
         "📚 Knowledge Gap Analysis",
         "📖 Documentation"]
    )
    
    st.markdown("---")
    st.caption("Using simulated data • No external connections needed")
    st.caption(f"Total Inquiries: {len(db.get_all_inquiries())}")

# Main content based on selected page
if page == "📊 Dashboard":
    st.title("📊 Developer Support Analytics")
    st.markdown("Analyzing patterns in carbon project developer inquiries")
    
    # Get stats
    stats = analyzer.get_summary_stats()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Inquiries", stats['total_inquiries'])
    with col2:
        st.metric("Resolution Rate", f"{stats['resolution_rate']}%")
    with col3:
        st.metric("Avg Response", f"{stats['avg_response_time']} hrs")
    with col4:
        st.metric("Escalation Rate", f"{stats['escalation_rate']}%")
    
    # Two charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📌 Inquiries by Category")
        if stats['top_categories']:
            cat_df = pd.DataFrame(
                list(stats['top_categories'].items()), 
                columns=['Category', 'Count']
            )
            fig = px.pie(cat_df, values='Count', names='Category', 
                         title='Distribution by Category',
                         color_discrete_sequence=px.colors.sequential.Greens_r)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Top Inquiry Intents")
        if stats['top_intents']:
            intent_df = pd.DataFrame(
                list(stats['top_intents'].items()), 
                columns=['Intent', 'Count']
            )
            fig = px.bar(intent_df, x='Intent', y='Count', 
                         title='Most Common Intents',
                         color='Count', color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent inquiries table
    st.subheader("📋 Recent Developer Inquiries")
    df = pd.DataFrame(db.get_all_inquiries()[-10:])
    display_cols = ['date', 'user_type', 'category', 'intent', 'status', 'response_time_hours']
    st.dataframe(
        df[display_cols].rename(columns={
            'response_time_hours': 'Resp Time (hrs)'
        }),
        use_container_width=True,
        hide_index=True
    )

elif page == "🔍 Inquiry Analysis":
    st.title("🔍 Deep Inquiry Analysis")
    
    df = pd.DataFrame(db.get_all_inquiries())
    
    # Filters
    with st.expander("🔎 Filter Inquiries", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            categories = ['All'] + sorted(df['category'].unique().tolist())
            selected_category = st.selectbox("Category", categories)
        
        with col2:
            statuses = ['All'] + sorted(df['status'].unique().tolist())
            selected_status = st.selectbox("Status", statuses)
        
        with col3:
            user_types = ['All'] + sorted(df['user_type'].unique().tolist())
            selected_user = st.selectbox("User Type", user_types)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if selected_user != 'All':
        filtered_df = filtered_df[filtered_df['user_type'] == selected_user]
    
    # Show results
    st.subheader(f"📋 Results ({len(filtered_df)} inquiries)")
    
    # Format for display
    display_df = filtered_df[[
        'date', 'inquiry_id', 'user_type', 'category', 
        'intent', 'status', 'complexity', 'response_time_hours'
    ]].copy()
    
    display_df.columns = ['Date', 'ID', 'User Type', 'Category', 
                         'Intent', 'Status', 'Complexity', 'Resp Time (hrs)']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Export option
    if st.button("📥 Export as CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"inquiries_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

elif page == "🤖 Training Data Generator":
    st.title("🤖 AI Training Data Generator")
    st.markdown("Create labeled training examples for the support agent")
    
    training_data = analyzer.extract_training_pairs()
    
    # Quality filter
    quality_filter = st.selectbox(
        "Filter by Quality",
        ["All", "high", "medium", "low"]
    )
    
    if quality_filter != "All":
        training_data = [t for t in training_data if t['quality_flag'] == quality_filter]
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Examples", len(training_data))
    with col2:
        high_quality = len([t for t in training_data if t['quality_flag'] == 'high'])
        st.metric("High Quality", high_quality)
    with col3:
        intent_coverage = len(set([t['intent'] for t in training_data]))
        st.metric("Intent Coverage", intent_coverage)
    
    # Show data
    if training_data:
        train_df = pd.DataFrame(training_data)
        st.dataframe(train_df, use_container_width=True, hide_index=True)
        
        # Download button
        if st.button("Generate Training File"):
            # Format for fine-tuning (simplified JSONL)
            training_jsonl = []
            for item in training_data[:20]:  # Limit for demo
                training_jsonl.append({
                    "messages": [
                        {"role": "user", "content": item['prompt']},
                        {"role": "assistant", "content": f"[TRAINING EXAMPLE] Category: {item['category']}, Intent: {item['intent']}, Project Type: {item['project_type']}"}
                    ]
                })
            
            # Convert to JSONL string
            jsonl_str = "\n".join([str(x) for x in training_jsonl])
            
            st.download_button(
                label="📥 Download Training Data (JSONL)",
                data=jsonl_str,
                file_name="training_data.jsonl",
                mime="application/jsonl"
            )
    else:
        st.info("No training data matches the selected filter")

elif page == "🧪 Agent Testing":
    st.title("🧪 AI Agent Testing Framework")
    st.markdown("Test agent responses and identify failure patterns")
    
    # Test configuration
    col1, col2 = st.columns(2)
    with col1:
        test_size = st.slider("Number of test inquiries", 5, 30, 15)
    with col2:
        test_category = st.selectbox(
            "Test specific category (optional)",
            ["All"] + sorted(list(set([i['category'] for i in db.get_all_inquiries()])))
        )
    
    if st.button("🚀 Run Test Suite", type="primary"):
        with st.spinner("Testing agent responses..."):
            # Get test inquiries
            all_inquiries = db.get_all_inquiries()
            
            if test_category != "All":
                test_inquiries = [i for i in all_inquiries if i['category'] == test_category]
            else:
                test_inquiries = all_inquiries
            
            # Random sample
            test_inquiries = random.sample(test_inquiries, min(test_size, len(test_inquiries)))
            
            # Run tests
            results = tester.run_test_suite(test_inquiries)
            report = tester.generate_test_report(results)
            
            # Display results
            st.subheader("📋 Test Results Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Tests Run", report['summary']['total_tests'])
            with col2:
                st.metric("Pass Rate", f"{report['summary']['pass_rate']}%")
            with col3:
                st.metric("Avg Quality", report['summary']['avg_quality_score'])
            with col4:
                st.metric("Failed", report['summary']['failed'])
            
            # Category breakdown
            if report['by_category']:
                st.subheader("📊 Performance by Category")
                cat_df = pd.DataFrame([
                    {"Category": cat, "Pass Rate": f"{data['pass_rate']}%", "Avg Quality": data['avg_quality']}
                    for cat, data in report['by_category'].items()
                ])
                st.dataframe(cat_df, use_container_width=True, hide_index=True)
            
            # Failure patterns
            if report['failure_patterns']:
                st.subheader("⚠️ Failure Patterns")
                for pattern in report['failure_patterns']:
                    if "message" in pattern:
                        st.success(pattern["message"])
                    else:
                        with st.expander(f"🔴 {pattern['category']} - {pattern['failure_count']} failures"):
                            st.write("**Common Issues:**", ", ".join(pattern['common_issues']))
                            st.write("**Recommendation:**", pattern['recommendation'])
            
            # Detailed results
            with st.expander("🔬 View Detailed Test Results"):
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True, hide_index=True)

elif page == "📚 Knowledge Gap Analysis":
    st.title("📚 Knowledge Gap Identification")
    st.markdown("Find missing documentation based on inquiry patterns")
    
    gaps = analyzer.identify_knowledge_gaps()
    
    if gaps:
        for gap in gaps:
            severity_color = "🔴" if gap['gap_severity'] == 'high' else "🟡"
            
            with st.container():
                st.subheader(f"{severity_color} {gap['category'].replace('_', ' ').title()}")
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric("Escalations", gap['escalation_count'])
                    if gap['priority'] == 1:
                        st.error("HIGH PRIORITY")
                    else:
                        st.warning("MEDIUM PRIORITY")
                
                with col2:
                    if gap['sample_questions']:
                        st.write("**Sample questions from developers:**")
                        for q in gap['sample_questions']:
                            st.write(f"- _{q}_")
                    
                    st.write("**Recommendation:**", gap['recommendation'])
                
                st.markdown("---")
    else:
        st.success("✅ No major knowledge gaps detected! The knowledge base appears comprehensive.")

else:  # Documentation
    st.title("📖 Knowledge Base & Documentation")
    
    # Show current documentation
    st.subheader("Current Registry Documentation")
    
    tab1, tab2, tab3 = st.tabs(["Methodologies", "Registration Steps", "FAQs"])
    
    with tab1:
        st.markdown("### Approved Methodologies")
        for code, desc in db.knowledge_base['methodologies'].items():
            with st.expander(f"📄 {code}"):
                st.write(desc)
    
    with tab2:
        st.markdown("### Project Registration Process")
        for step in db.knowledge_base['registration_steps']:
            st.write(step)
    
    with tab3:
        st.markdown("### Frequently Asked Questions")
        for question, answer in db.knowledge_base['faqs'].items():
            with st.expander(f"❓ {question}"):
                st.write(answer)
    
    # Documentation update tool
    st.markdown("---")
    st.subheader("📝 Suggest Documentation Update")
    
    with st.form("doc_suggestion"):
        topic = st.text_input("Topic needing documentation")
        why_needed = st.text_area("Why is this needed? (common questions, confusion points)")
        
        if st.form_submit_button("Submit Suggestion"):
            st.success("✅ Documentation suggestion recorded! This will be reviewed for the next update.")