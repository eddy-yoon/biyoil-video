import streamlit as st
from moviepy.editor import ImageClip, concatenate_videoclips, vfx
import tempfile
import os

st.set_page_config(page_title="비요일 영상 제작소", page_icon="☔")
st.title("☔ 비요일(Biyoil) 숏폼 자동 제작기")
st.write("이미지를 올리면 4050 감성의 영상을 자동으로 만듭니다.")

# 파일 업로드
images = st.file_uploader("제품 사진들을 여러 장 선택하세요", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
logo = st.file_uploader("브랜드 로고(비요일) 이미지를 올려주세요", type=['jpg', 'jpeg', 'png'])

if st.button("영상 생성 시작"):
    if images and logo:
        with st.spinner('영상을 우아하게 제작 중입니다... 잠시만 기다려 주세요.'):
            clips = []
            
            # 1. 사진 클립 생성
            for img in images:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tfile:
                    tfile.write(img.read())
                    # 9:16 비율(세로형)에 맞춰 리사이징
                    clip = ImageClip(tfile.name).set_duration(1.5).resize(height=1920)
                    clip = clip.set_fps(24).crossfadein(0.5)
                    clips.append(clip)
            
            # 2. 로고 엔딩 (3초, 서서히 확대되는 무빙)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as lfile:
                lfile.write(logo.read())
                logo_clip = ImageClip(lfile.name).set_duration(3).resize(height=1920)
                logo_clip = logo_clip.fx(vfx.resize, lambda t: 1 + 0.03 * t) 
                logo_clip = logo_clip.set_fps(24).crossfadein(1.0)
                clips.append(logo_clip)
            
            # 3. 영상 합치기
            final_video = concatenate_videoclips(clips, method="compose")
            output_path = "biyoil_final.mp4"
            final_video.write_videofile(output_path, fps=24, codec="libx264")
            
            st.video(output_path)
            st.success("완성! 영상을 마우스 우클릭하여 저장하세요.")
    else:
        st.error("사진과 로고를 모두 등록해주세요.")
