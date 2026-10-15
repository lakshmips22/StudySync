from __future__ import annotations

from datetime import date, datetime, timedelta
import io

import pandas as pd
import plotly.express as px
import streamlit as st

import database as db

st.set_page_config(page_title="StudySync · Smart Study Planner", page_icon="📚", layout="wide", initial_sidebar_state="expanded")
db.init_db()

st.markdown("""
<style>
:root{--ink:#17253f;--muted:#73819a;--blue:#4e72e8;--pale:#f4f7fc;--line:#e8edf5}
html,body,[class*="css"]{font-family:'Segoe UI',Arial,sans-serif;color:var(--ink)}
.stApp{background:#f6f8fc}.block-container{padding-top:1.65rem;max-width:1440px}
h1,h2,h3{font-family:'Segoe UI',Arial,sans-serif;letter-spacing:-.035em;color:var(--ink)}
.hero{background:linear-gradient(115deg,#243a67 0%,#4265bd 60%,#6082df 100%);border-radius:22px;padding:30px 34px;color:white;margin-bottom:20px;box-shadow:0 12px 32px #344e8426}
.hero h1{color:white;font-size:30px;margin:0 0 5px}.hero p{color:#dbe5ff;margin:0;font-size:14px}
.eyebrow{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#abbff8;margin-bottom:9px}
.metric{background:white;border:1px solid var(--line);border-radius:17px;padding:19px 20px;min-height:124px;box-shadow:0 4px 15px #243b6510}
.metric-label{color:var(--muted);font-size:12px;font-weight:600}.metric-value{font:800 28px 'Segoe UI',Arial,sans-serif;color:var(--ink);margin:8px 0 2px}.metric-foot{font-size:11px;color:#94a0b3}
.panel{background:white;border:1px solid var(--line);border-radius:18px;padding:20px 22px;margin-bottom:16px;box-shadow:0 4px 15px #243b6508}
.taskrow{background:white;border:1px solid var(--line);border-radius:14px;padding:15px 17px;margin:8px 0;display:flex;align-items:center;gap:12px}
.pill{display:inline-block;padding:4px 9px;border-radius:99px;background:#eff3fb;color:#58709c;font-size:11px;font-weight:700}
.small-muted{color:var(--muted);font-size:12px}.stButton button{border-radius:10px;font-weight:600}.stDownloadButton button{border-radius:10px}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
div[data-testid="stMetric"]{background:white;border:1px solid var(--line);padding:15px 18px;border-radius:16px}
.stTabs [data-baseweb="tab-list"]{gap:10px}.stTabs [data-baseweb="tab"]{border-radius:10px}
</style>
""", unsafe_allow_html=True)

def csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode('utf-8-sig')

def deadline_label(value: str) -> tuple[str, str]:
    due = date.fromisoformat(str(value)[:10]); today = date.today()
    if due < today: return 'Overdue', '🔴'
    if due == today: return 'Due today', '🟠'
    if due == today + timedelta(days=1): return 'Tomorrow', '🟡'
    return due.strftime('%b %d'), '🔵'

def hero(title: str, subtitle: str):
    st.markdown(f'<div class="hero"><div class="eyebrow">STUDYSYNC · SMART STUDY PLANNER</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def metric(label: str, value: str, foot: str = ''):
    st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>', unsafe_allow_html=True)

def load_data():
    return db.subjects(), db.tasks(), db.sessions()

def sidebar_nav():
    with st.sidebar:
        st.markdown("<div style='font:800 23px Segoe UI,Arial,sans-serif;color:#263a63;padding:6px 4px 0'>📚 StudySync</div><div style='color:#8592a8;font-size:12px;padding:2px 4px 18px'>Smart Study Planner</div>", unsafe_allow_html=True)
        page = st.radio('Workspace', ['🏠  Dashboard','📚  Subjects','📝  Tasks','⏱️  Study Sessions','📊  Analytics','⚙️  Settings'], label_visibility='collapsed')
        st.markdown('<div style="height:1px;background:#e8edf5;margin:14px 0"></div>', unsafe_allow_html=True)
        sub, tasks, sessions = load_data()
        completed = int((tasks.status == 'Completed').sum()) if not tasks.empty else 0
        st.caption('YOUR MOMENTUM')
        st.progress(completed / max(len(tasks),1))
        st.caption(f'{completed} of {len(tasks)} tasks complete')
        st.markdown('<div style="height:1px;background:#e8edf5;margin:14px 0"></div>', unsafe_allow_html=True)
        st.caption(f'📚 {len(sub)} subjects  ·  ⏱️ {int(sessions.duration_minutes.sum()) if not sessions.empty else 0} min studied')
        return page

def dashboard():
    subjects, tasks, sessions = load_data()
    hour = datetime.now().hour
    greeting = 'Good morning' if hour < 12 else ('Good afternoon' if hour < 18 else 'Good evening')
    hero(f'{greeting}! Ready to make progress today?', 'A little progress each day adds up to big results. Here’s your study snapshot.')
    today = date.today().isoformat()
    if tasks.empty:
        completed = pending = due_today = overdue = 0; pct = 0
    else:
        completed = int((tasks.status == 'Completed').sum()); pending = len(tasks)-completed
        due_today = int(((tasks.deadline == today) & (tasks.status != 'Completed')).sum())
        overdue = int(((tasks.deadline < today) & (tasks.status != 'Completed')).sum())
        pct = round(completed / len(tasks) * 100)
    cards = st.columns(5)
    for col, label, value, foot in zip(cards, ['Subjects','Study tasks','Completed','Pending','Overall progress'], [str(len(subjects)),str(len(tasks)),str(completed),str(pending),f'{pct}%'], ['Your learning tracks','Across every subject','Nice work so far','Ready when you are','Keep your streak going']):
        with col: metric(label,value,foot)
    st.write('')
    left,right=st.columns([1.35,1])
    with left:
        st.markdown('<div class="panel"><h3 style="margin:0">📈 Progress at a glance</h3><div class="small-muted">Completed and remaining work</div>',unsafe_allow_html=True)
        if tasks.empty: st.info('No study tasks yet. Add your first task to see your progress take shape.')
        else:
            chart=pd.DataFrame({'Status':['Completed','In progress','Pending'],'Tasks':[int((tasks.status=='Completed').sum()),int((tasks.status=='In Progress').sum()),int((tasks.status=='Pending').sum())]})
            fig=px.pie(chart,names='Status',values='Tasks',hole=.70,color='Status',color_discrete_map={'Completed':'#43b58b','In progress':'#6385ec','Pending':'#dce4f2'})
            fig.update_traces(textinfo='none',hovertemplate='%{label}: %{value}<extra></extra>'); fig.update_layout(height=250,margin=dict(t=8,b=8,l=8,r=8),showlegend=True,legend=dict(orientation='h',y=-.12),paper_bgcolor='white',plot_bgcolor='white')
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            st.progress(completed/max(len(tasks),1),text=f'{pct}% overall completion')
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><h3 style="margin:0">📚 Subject progress</h3><div class="small-muted">A quick view of each course</div>',unsafe_allow_html=True)
        if subjects.empty: st.info('Add your first subject to get started.')
        else:
            for _,s in subjects.iterrows():
                n=int(s.task_count); done=int(s.completed_count); rate=done/n if n else 0
                st.markdown(f"<div style='display:flex;justify-content:space-between;margin-top:12px'><span>{s.icon} <b>{s.name}</b></span><span class='small-muted'>{done}/{n}</span></div>",unsafe_allow_html=True)
                st.progress(rate)
        st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><h3 style="margin:0">🎯 Today’s Focus</h3><div class="small-muted">Priority tasks sorted by urgency</div>',unsafe_allow_html=True)
    focus=tasks[tasks.status!='Completed'].copy() if not tasks.empty else tasks
    if not focus.empty:
        focus['_priority']=focus.priority.map({'High':0,'Medium':1,'Low':2})
        focus=focus.sort_values(['deadline','_priority']).head(4)
        for _,t in focus.iterrows():
            label,icon=deadline_label(t.deadline)
            c1,c2,c3=st.columns([5,2,1])
            c1.markdown(f"**{t.subject_icon} {t.title}**  \n<span class='small-muted'>{t.subject} · {t.priority} priority</span>",unsafe_allow_html=True)
            c2.markdown(f'{icon} {label}')
            if c3.button('Done',key=f'focus_done_{t.id}'):
                db.set_task_status(int(t.id),'Completed'); st.rerun()
    else: st.success('Nothing urgent right now. Add a task or enjoy the breathing room!')
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><h3 style="margin:0">🗓️ Upcoming deadlines</h3><div class="small-muted">Your next study milestones</div>',unsafe_allow_html=True)
    upcoming=tasks[(tasks.status!='Completed') & (tasks.deadline>=today)].sort_values('deadline').head(5) if not tasks.empty else tasks
    if upcoming.empty: st.caption('No upcoming deadlines. You’re all caught up.')
    else:
        for _,t in upcoming.iterrows():
            label,icon=deadline_label(t.deadline)
            st.markdown(f"{icon} **{t.title}** · {t.subject} <span class='pill'>{label}</span>",unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

def subjects_page():
    subjects,tasks,_=load_data(); hero('Your subjects','Organise your courses and see how each one is moving forward.')
    with st.expander('＋ Add a subject',expanded=subjects.empty):
        with st.form('add_subject',clear_on_submit=True):
            name=st.text_input('Subject name',placeholder='e.g. Human Computer Interaction')
            c1,c2=st.columns([1,3]); color=c1.color_picker('Subject color','#5B8DEF'); icon=c2.selectbox('Icon',['📘','🧠','💻','🌐','📐','🤖','🧪','📝','🎨','📊'])
            submitted=st.form_submit_button('Add subject',type='primary')
        if submitted:
            if not name.strip(): st.error('Please enter a subject name.')
            elif name.strip().casefold() in subjects.name.str.casefold().tolist(): st.error('A subject with that name already exists.')
            else:
                db.add_subject(name,color,icon); st.success(f'{name.strip()} added.'); st.rerun()
    if subjects.empty:
        st.info('Add your first subject to get started. Subjects help you organise tasks and study time.')
        return
    for _,s in subjects.iterrows():
        rate=int(round(100*int(s.completed_count)/int(s.task_count))) if s.task_count else 0
        with st.container(border=True):
            col1,col2=st.columns([4,1]); col1.markdown(f"### {s.icon} {s.name}"); col1.caption(f"{s.task_count} tasks · {s.completed_count} completed")
            col1.progress(rate,text=f'{rate}% complete')
            with col2:
                if st.button('Edit',key=f'sub_edit_{s.id}'): st.session_state['editing_subject']=int(s.id)
                if st.button('Delete',key=f'sub_del_{s.id}'):
                    st.session_state['delete_subject']=int(s.id)
        if st.session_state.get('editing_subject')==int(s.id):
            with st.form(f'edit_subject_{s.id}'):
                new_name=st.text_input('Name',value=s['name']); c1,c2=st.columns([1,3]); new_color=c1.color_picker('Color',value=s.color); new_icon=c2.selectbox('Icon',['📘','🧠','💻','🌐','📐','🤖','🧪','📝','🎨','📊'],index=['📘','🧠','💻','🌐','📐','🤖','🧪','📝','🎨','📊'].index(s.icon) if s.icon in ['📘','🧠','💻','🌐','📐','🤖','🧪','📝','🎨','📊'] else 0)
                a,b=st.columns(2); save=a.form_submit_button('Save changes',type='primary'); cancel=b.form_submit_button('Cancel')
            if save:
                if not new_name.strip(): st.error('Subject name is required.')
                elif new_name.strip().casefold() in [n.casefold() for n in subjects.name.tolist() if n.casefold()!=s['name'].casefold()]: st.error('That subject name is already in use.')
                else: db.update_subject(int(s.id),new_name,new_color,new_icon); st.session_state.pop('editing_subject',None); st.rerun()
            if cancel: st.session_state.pop('editing_subject',None); st.rerun()
    sid=st.session_state.get('delete_subject')
    if sid:
        target=subjects[subjects.id==sid]
        if not target.empty:
            st.warning(f"Delete **{target.iloc[0]['name']}**? Its associated tasks and study sessions will also be removed.")
            a,b=st.columns(2)
            if a.button('Confirm delete subject',type='primary'): db.delete_subject(sid); st.session_state.pop('delete_subject',None); st.rerun()
            if b.button('Keep subject'): st.session_state.pop('delete_subject',None); st.rerun()

def task_editor(subjects: pd.DataFrame, task=None):
    editing=task is not None
    opts={f"{r.icon} {r.name}":int(r.id) for _,r in subjects.iterrows()}
    form_key = f'task_form_{int(task.id)}' if editing else 'task_form_new'
    with st.form(form_key,clear_on_submit=not editing):
        title=st.text_input('Task or topic name',value=task.title if editing else '',placeholder='e.g. Complete linked list exercises')
        sublabels=list(opts); idx=next((i for i,x in enumerate(sublabels) if opts[x]==int(task.subject_id)),0) if editing else 0
        subject_label=st.selectbox('Subject',sublabels,index=idx)
        description=st.text_area('Description / notes',value=task.description if editing else '',placeholder='Add a few helpful details…')
        c1,c2,c3=st.columns(3)
        rawdate=date.fromisoformat(str(task.deadline)[:10]) if editing else date.today()+timedelta(days=1)
        deadline=c1.date_input('Deadline',value=rawdate,min_value=date(2000,1,1),max_value=date(2100,12,31))
        priority=c2.selectbox('Priority',['Low','Medium','High'],index=['Low','Medium','High'].index(task.priority) if editing else 1)
        status=c3.selectbox('Status',['Pending','In Progress','Completed'],index=['Pending','In Progress','Completed'].index(task.status) if editing else 0)
        a,b=st.columns(2); save=a.form_submit_button('Save task' if editing else '＋ Add task',type='primary'); cancel=b.form_submit_button('Cancel') if editing else False
    if save:
        if not title.strip(): st.error('Task name is required.')
        elif not subject_label: st.error('Choose a subject first.')
        elif deadline is None: st.error('Choose a valid deadline.')
        else:
            db.save_task(int(task.id) if editing else None,title,opts[subject_label],description,deadline,priority,status)
            st.session_state.pop('editing_task',None); st.success('Task saved.'); st.rerun()
    if cancel: st.session_state.pop('editing_task',None); st.rerun()

def tasks_page():
    subjects,tasks,_=load_data(); hero('Your study tasks','Capture the work, set a deadline, and keep momentum visible.')
    if subjects.empty:
        st.info('Add a subject before creating a study task.'); return
    with st.expander('＋ Create a study task',expanded=tasks.empty): task_editor(subjects)
    with st.container(border=True):
        a,b,c,d=st.columns([2,1,1,1]); query=a.text_input('Search tasks',placeholder='Search by topic or notes…',label_visibility='collapsed')
        subject_opts=['All subjects']+subjects.name.tolist(); subject_filter=b.selectbox('Subject',subject_opts,label_visibility='collapsed')
        priority_filter=c.selectbox('Priority',['All priorities','High','Medium','Low'],label_visibility='collapsed')
        status_filter=d.selectbox('Status',['All statuses','Pending','In Progress','Completed'],label_visibility='collapsed')
        a,b,c=st.columns(3); date_filter=a.selectbox('Deadline',['Any date','Overdue','Due today','Due tomorrow','Upcoming (next 7 days)']); sort=a.selectbox('Sort by',['Soonest deadline','Priority','Newest first']); show=a.selectbox('Show',['All tasks','Open tasks only','Completed only'])
    filtered=tasks.copy()
    if query.strip(): filtered=filtered[filtered.title.str.contains(query.strip(),case=False,na=False)|filtered.description.str.contains(query.strip(),case=False,na=False)]
    if subject_filter!='All subjects': filtered=filtered[filtered.subject==subject_filter]
    if priority_filter!='All priorities': filtered=filtered[filtered.priority==priority_filter]
    if status_filter!='All statuses': filtered=filtered[filtered.status==status_filter]
    today=date.today().isoformat(); tomorrow=(date.today()+timedelta(days=1)).isoformat(); nextweek=(date.today()+timedelta(days=7)).isoformat()
    if date_filter=='Overdue': filtered=filtered[(filtered.deadline<today)&(filtered.status!='Completed')]
    elif date_filter=='Due today': filtered=filtered[(filtered.deadline==today)&(filtered.status!='Completed')]
    elif date_filter=='Due tomorrow': filtered=filtered[(filtered.deadline==tomorrow)&(filtered.status!='Completed')]
    elif date_filter.startswith('Upcoming'): filtered=filtered[(filtered.deadline>=tomorrow)&(filtered.deadline<=nextweek)&(filtered.status!='Completed')]
    if show=='Open tasks only': filtered=filtered[filtered.status!='Completed']
    elif show=='Completed only': filtered=filtered[filtered.status=='Completed']
    if sort=='Priority': filtered['_sort']=filtered.priority.map({'High':0,'Medium':1,'Low':2}); filtered=filtered.sort_values(['_sort','deadline'])
    elif sort=='Newest first': filtered=filtered.sort_values('created_at',ascending=False)
    else: filtered=filtered.sort_values(['deadline','priority'])
    st.caption(f'{len(filtered)} task{"s" if len(filtered)!=1 else ""} shown')
    editing_id=st.session_state.get('editing_task')
    if editing_id and editing_id in tasks.id.tolist():
        st.markdown('#### Edit task'); task_editor(subjects,tasks[tasks.id==editing_id].iloc[0])
    if filtered.empty: st.info('No study tasks match these filters. Try changing a filter or add a task above.')
    for _,t in filtered.iterrows():
        with st.container(border=True):
            c1,c2,c3,c4=st.columns([4,1.3,1.25,1.35]); c1.markdown(f"**{t.subject_icon} {t.title}**  \n<span class='small-muted'>{t.subject} · {t.priority} priority</span>",unsafe_allow_html=True)
            label,icon=deadline_label(t.deadline); c2.markdown(f'{icon} {label}')
            new_status=c3.selectbox('Status',['Pending','In Progress','Completed'],index=['Pending','In Progress','Completed'].index(t.status),key=f'status_{t.id}',label_visibility='collapsed')
            if new_status!=t.status: db.set_task_status(int(t.id),new_status); st.rerun()
            b1,b2=c4.columns(2)
            if b1.button('✏️',key=f'edit_{t.id}',help='Edit task'): st.session_state['editing_task']=int(t.id); st.rerun()
            if b2.button('🗑️',key=f'delete_{t.id}',help='Delete task'): st.session_state['delete_task']=int(t.id)
            if t.description: st.caption(t.description)
            if st.session_state.get('delete_task')==int(t.id):
                st.warning(f'Delete “{t.title}”?')
                x,y=st.columns(2)
                if x.button('Confirm delete',key=f'confirm_del_{t.id}',type='primary'): db.delete_task(int(t.id)); st.session_state.pop('delete_task',None); st.rerun()
                if y.button('Cancel delete',key=f'cancel_del_{t.id}'): st.session_state.pop('delete_task',None); st.rerun()

def sessions_page():
    subjects,_,sessions=load_data(); hero('Study sessions','Log focused time and build a record of your effort.')
    total=int(sessions.duration_minutes.sum()) if not sessions.empty else 0
    metric('Total Study Time',f'{total//60}h {total%60:02d}m',f'{len(sessions)} sessions logged')
    st.write('')
    if subjects.empty: st.info('Add a subject before logging a study session.'); return
    with st.expander('＋ Log a study session',expanded=sessions.empty):
        with st.form('session_form',clear_on_submit=True):
            opts={f'{r.icon} {r.name}':int(r.id) for _,r in subjects.iterrows()}; chosen=st.selectbox('Subject',list(opts))
            c1,c2=st.columns(2); minutes=c1.number_input('Duration (minutes)',min_value=1,max_value=1440,value=30,step=5); when=c2.date_input('Study date',value=date.today(),min_value=date(2000,1,1),max_value=date.today())
            notes=st.text_input('Session note (optional)',placeholder='e.g. Practised recursion problems')
            submitted=st.form_submit_button('Save session',type='primary')
        if submitted:
            if int(minutes)<1: st.error('Duration must be at least one minute.')
            else: db.add_session(opts[chosen],int(minutes),notes,datetime.combine(when,datetime.now().time())); st.success('Study session saved.'); st.rerun()
    left,right=st.columns([1,1.1])
    with left:
        st.markdown('<div class="panel"><h3 style="margin:0">Time by subject</h3>',unsafe_allow_html=True)
        if sessions.empty: st.info('Your subject study totals will appear here.')
        else:
            by=sessions.groupby('subject',as_index=False).duration_minutes.sum().sort_values('duration_minutes',ascending=True)
            fig=px.bar(by,x='duration_minutes',y='subject',orientation='h',color='subject',color_discrete_sequence=px.colors.qualitative.Safe,labels={'duration_minutes':'Minutes','subject':''})
            fig.update_layout(height=max(230,40*len(by)),showlegend=False,margin=dict(t=8,b=8,l=8,r=8),paper_bgcolor='white',plot_bgcolor='white'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><h3 style="margin:0">Recent sessions</h3>',unsafe_allow_html=True)
        if sessions.empty: st.info('No sessions yet. Log your first focused study block.')
        else:
            for _,s in sessions.head(8).iterrows():
                dt=datetime.fromisoformat(s.studied_at).strftime('%b %d · %I:%M %p')
                st.markdown(f"**{s.subject}** · {int(s.duration_minutes)} min  \n<span class='small-muted'>{dt}{' · '+s.notes if s.notes else ''}</span>",unsafe_allow_html=True); st.markdown('<hr style="margin:8px 0;border-color:#edf0f6">',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

def analytics_page():
    subjects,tasks,sessions=load_data(); hero('Your progress, in perspective','Understand what you’ve completed and where your study time goes.')
    completed=int((tasks.status=='Completed').sum()) if not tasks.empty else 0; pct=round(100*completed/len(tasks)) if len(tasks) else 0
    a,b,c=st.columns(3)
    with a: metric('Overall completion',f'{pct}%','Completed tasks / all tasks')
    with b: metric('Tasks completed',str(completed),f'of {len(tasks)} total tasks')
    with c: metric('Total study time',f'{int(sessions.duration_minutes.sum()) if not sessions.empty else 0} min',f'{len(sessions)} sessions')
    if tasks.empty: st.info('Add study tasks to unlock your progress analytics.')
    else:
        left,right=st.columns(2)
        with left:
            st.markdown('<div class="panel"><h3 style="margin:0">Subject-wise completion</h3>',unsafe_allow_html=True)
            data=subjects[['name','task_count','completed_count']].copy(); data['Completion %']=data.apply(lambda r:round(100*r.completed_count/r.task_count) if r.task_count else 0,axis=1)
            fig=px.bar(data,x='name',y='Completion %',color='name',range_y=[0,100],labels={'name':'Subject'},color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(height=330,showlegend=False,margin=dict(t=10,b=10),paper_bgcolor='white',plot_bgcolor='white'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False}); st.markdown('</div>',unsafe_allow_html=True)
        with right:
            st.markdown('<div class="panel"><h3 style="margin:0">Priority distribution</h3>',unsafe_allow_html=True)
            dist=tasks.groupby('priority',as_index=False).size().rename(columns={'size':'Tasks'})
            fig=px.pie(dist,names='priority',values='Tasks',hole=.55,color='priority',color_discrete_map={'High':'#e66b72','Medium':'#f3b44d','Low':'#5bba91'})
            fig.update_layout(height=330,margin=dict(t=12,b=12),paper_bgcolor='white',legend_title_text='Priority'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False}); st.markdown('</div>',unsafe_allow_html=True)
        completed_rows=tasks[tasks.status=='Completed'].copy()
        if not completed_rows.empty:
            completed_rows['completed_day']=pd.to_datetime(completed_rows.completed_at,errors='coerce').dt.date
            completed_rows=completed_rows.dropna(subset=['completed_day']).groupby('completed_day',as_index=False).size().rename(columns={'size':'Tasks completed'})
        st.markdown('<div class="panel"><h3 style="margin:0">Weekly progress</h3><div class="small-muted">Tasks completed during the last seven days</div>',unsafe_allow_html=True)
        days=pd.DataFrame({'completed_day':[date.today()-timedelta(days=n) for n in range(6,-1,-1)]})
        if not completed_rows.empty: days=days.merge(completed_rows,on='completed_day',how='left')
        else: days['Tasks completed']=0
        days['Tasks completed']=days['Tasks completed'].fillna(0).astype(int)
        fig=px.bar(days,x='completed_day',y='Tasks completed',labels={'completed_day':'Day'},color_discrete_sequence=['#5b7ce7'])
        fig.update_layout(height=290,margin=dict(t=8,b=8),paper_bgcolor='white',plot_bgcolor='white'); st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False}); st.markdown('</div>',unsafe_allow_html=True)

def settings_page():
    subjects,tasks,sessions=load_data(); hero('Settings & data','Keep control of your local study planner data.')
    st.markdown('<div class="panel"><h3 style="margin:0">Sample data</h3><div class="small-muted">Load a realistic starter workspace for a quick demonstration. Demo data is clearly sample content.</div>',unsafe_allow_html=True)
    if st.button('✨ Load demo data',type='primary',disabled=not subjects.empty):
        db.load_demo_data(); st.success('Demo workspace loaded.'); st.rerun()
    if not subjects.empty: st.caption('Demo loading is available when your workspace has no subjects. Export your data first if you need a copy.')
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><h3 style="margin:0">Export your data</h3><div class="small-muted">Download a CSV copy of any table.</div>',unsafe_allow_html=True)
    exports=[('Subjects',subjects.drop(columns=['task_count','completed_count'],errors='ignore'),'studysync_subjects.csv'),('Tasks',tasks,'studysync_tasks.csv'),('Study sessions',sessions,'studysync_sessions.csv')]
    cols=st.columns(3)
    for col,(label,data,filename) in zip(cols,exports):
        col.download_button(f'⬇️ {label} CSV',data=csv_bytes(data),file_name=filename,mime='text/csv',disabled=data.empty,use_container_width=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><h3 style="margin:0">About StudySync</h3><p class="small-muted">A local-first student productivity prototype. StudySync stores subjects, tasks, and study sessions in a SQLite database on this computer. No account or external service is required.</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="panel"><h3 style="margin:0;color:#a83c4c">Reset all data</h3><div class="small-muted">Permanently delete every subject, task, and study session from this local database.</div>',unsafe_allow_html=True)
    if not st.session_state.get('confirm_reset'):
        if st.button('Reset all data',type='secondary'): st.session_state['confirm_reset']=True; st.rerun()
    else:
        st.warning('This cannot be undone. Download CSV backups first if you want to keep a copy.')
        a,b=st.columns(2)
        if a.button('Yes, delete all data',type='primary'): db.reset_all(); st.session_state.pop('confirm_reset',None); st.success('All StudySync data has been reset.'); st.rerun()
        if b.button('Cancel'): st.session_state.pop('confirm_reset',None); st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)

page=sidebar_nav()
if page.startswith('🏠'): dashboard()
elif page.startswith('📚'): subjects_page()
elif page.startswith('📝'): tasks_page()
elif page.startswith('⏱️'): sessions_page()
elif page.startswith('📊'): analytics_page()
else: settings_page()
