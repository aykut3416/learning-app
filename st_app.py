import streamlit as st
import pandas as pd
from streamlit_player import st_player, _SUPPORTED_EVENTS
import random
from text_highlighter import text_highlighter
from st_click_detector import click_detector
import pickle
from wiktionaryparser import WiktionaryParser
import pickle
import numpy as np



def main():
    st.set_page_config(
     page_title="English Streams",
     page_icon="🎬",
     layout="wide",
     initial_sidebar_state="expanded"
 )
    @st.experimental_memo
    def load_data():
        file = open("easy.pickle", 'rb')
        parser = WiktionaryParser()
        return pd.read_pickle("clear_dataset.pickle"),pickle.load(file),parser

    def channel_change():
        st.session_state.filtered_list = np.where(df["produc"].isin(st.session_state.selected_items))[0]

    def create_content(line1,line2,line3):
        ind1=0
        ind2=0
        ind3=0
        start_html="""<p style="text-align: center; color:#2A2525; font-size: 30px;"><strong>"""
        end_html="</strong></p>"
        words1 = line1.split(" ")
        l1=start_html
        for word in words1:
            if word in easy_wl or not word.islower() or "'" in word :
                orta1=" "+word
            else:
                orta1=""" <a href="#" id="{}">{}</a>""".format(word,word) 
            l1=l1+orta1
        l1=l1+end_html

        words2 = line2.split(" ")
        l2=start_html
        for word in words2:
            if word in easy_wl or not word.islower()  or "'" in word :
                orta2=" "+word
            else:
                orta2=""" <a href="#" id="{}">{}</a>""".format(word,word) 
            l2=l2+orta2
        l2=l2+end_html

        words3 = line3.split(" ")
        l3=start_html
        for word in words3:
            if word in easy_wl or not word.islower() or "'" in word :
                orta3=" "+word
            else:
                orta3=""" <a href="#" id="{}">{}</a>""".format(word,word) 
            l3=l3+orta3
        l3=l3+end_html
        
        return """{}{}{}""".format(l1,l2,l3) 

    def vocab_fetcher(word):
        try:
            wiki=parser.fetch(word,"english")
            dict_list=[]
            for defs in wiki[0]['definitions']:
                new_dict={}
                new_dict["type"]=defs["partOfSpeech"]
                new_dict["description"]=defs["text"][1]

                for rel in defs["relatedWords"]:
                    if rel['relationshipType']=='synonyms':
                        new_dict["synonyms"]=rel['words']
                    elif rel['relationshipType']=='related terms':
                        new_dict["related_wl"]=rel['words']
                if len(defs["examples"])>0:
                    max_ex=min(len(defs['examples']),3)
                    new_dict['examples']=defs["examples"][:max_ex]
                dict_list.append(new_dict)
            return markup_generator(dict_list)
        except:
            return markup_generator([])

    def markup_generator(definition_list):
        if len(definition_list)<1:
            return {}
        else:
            defs={}
            for feat in definition_list:
                all_str=""
                for key in feat.keys():
                    if key=="type":                
                        line="""\n __Part of speech__ : """+feat["type"].upper()+"\n"
                        all_str+=line
                    elif key=="description":
                        line="- __Description__ : "+feat["description"].capitalize()+"\n"
                        all_str+=line
                    elif key=="synonyms" and feat["synonyms"]!=[]:
                        line="- __Synonyms__ :"+"\n"
                        all_str+=line
                        line=" , ".join(feat["synonyms"])+"\n"
                        all_str+=line
                    elif key=="related_wl" and feat["related_wl"]!=[]:
                        line="- __Related words__ :"+"\n"
                        all_str+=line
                        line=" , ".join(feat["related_wl"])+"\n"
                        all_str+=line
                    elif key=="examples" and feat["examples"]!=[]:
                        line="- Example sentences :"+"\n"
                        all_str+=line
                        for ind,rw in enumerate(feat["examples"]):
                            line=str(ind+1)+" - "+rw+" \n "
                            all_str+=line
                defs[feat["type"].upper()]=all_str
            return defs
    
    def change_seq():
        st.session_state.current_ind=random.choice(st.session_state.filtered_list)
        st.session_state.old_row = -1
    
    def stop_play():
        st.session_state.playing=False
    
    def continue_play():
        st.session_state.playing=True
    
    def update_word():
            st.session_state.curr_word = st.session_state.search_key 
            st.session_state.curr_result = vocab_fetcher(st.session_state.curr_word)
        
    df,easy_wl,parser=load_data()
    
    c1, c2, c3 = st.columns([2,4, 1])
             
    if 'filtered_list' not in st.session_state:
        st.session_state.filtered_list = range(len(df))
    if 'current_ind' not in st.session_state:
        st.session_state.current_ind = random.randint(0,len(df))
    if 'playing' not in st.session_state:
        st.session_state.playing = True
    if 'curr_result' not in st.session_state:
        st.session_state.curr_result = {}
    if 'curr_word' not in st.session_state:
        st.session_state.curr_word = ""
    if 'search_key' not in st.session_state:
        st.session_state.search_key = ""
    if 'selected_items' not in st.session_state:
        st.session_state.selected_items = list(df.produc.unique())
    if 'content' not in st.session_state:
        st.session_state.content = create_content(" "," "," ")
    if 'old_time' not in st.session_state:
        st.session_state.old_time = 0
    if 'old_row' not in st.session_state:
        st.session_state.old_row = -1
    options = {
            "height":500,
            "events": ["onProgress","onPlay","onPause"],
            "progress_interval": 500,
            "playing": st.session_state.playing,
            "loop":  False,
            "controls": True,
            "muted": False,
            "play_inline":False
        }
    
    url=df.iloc[st.session_state.current_ind].url
    text_list=df.iloc[st.session_state.current_ind].text_list
    time_list=df.iloc[st.session_state.current_ind].end_time
 
    with c1:
        txt = st.text_input("",max_chars=25)
        if st.button("Manual Search"):
            st.session_state.search_key = txt
            update_word()
            if st.session_state.curr_result=={}:
                c1.write(st.session_state.curr_word+" is not found in the dictionary.")
            for feat in st.session_state.curr_result.keys():
                expander = c1.expander(st.session_state.curr_word+" as "+feat)
                expander.markdown(st.session_state.curr_result[feat])
            
        
        
 
        
          
    with c2:
        
        event = st_player(url, **options, key="youtube_player")

        clicked = click_detector(st.session_state.content)
        if clicked!="":
            st.session_state.search_key = clicked
            update_word()
            if st.session_state.curr_result=={}:
                c1.write(st.session_state.curr_word+" is not found in the dictionary.")
            for feat in st.session_state.curr_result.keys():
                expander = c1.expander(st.session_state.curr_word+" as "+feat)
                expander.markdown(st.session_state.curr_result[feat])
            clicked=""

        if event.name == "onPlay":
            st.session_state.playing=True
        if event.name == "onPause":
            st.session_state.playing=False
        
        if event.name=="onProgress" and abs(event.data["playedSeconds"]-st.session_state.old_time)>0.5:
            st.session_state.old_time = event.data["playedSeconds"]
            for i,t in enumerate(time_list[2::3]):
                if (event.data["playedSeconds"]+0.5)< t:
                    break
            if i!=st.session_state.old_row:
                st.session_state.old_row=i
                st.session_state.content = create_content(text_list[i*3],text_list[i*3+1],text_list[i*3+2])
           
    with c3:

        st.session_state.selected_items = st.multiselect(
            'Which series do you wanna watch?',
            list(df.produc.unique()),
            list(df.produc.unique()),on_change=channel_change)
        st.button('Next',on_click=change_seq)
        st.button('Play',on_click=continue_play)
        st.button('Stop',on_click=stop_play)
        


  

if __name__ == "__main__":
    main()