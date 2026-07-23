import streamlit as st
import PIL.Image
import os
import tempfile

# [필독] 최신 Pillow 버전에서 발생하는 ANTIALIAS 에러 방지 패치
if not hasattr(PIL.Image, 'Resampling'):
    PIL.Image.Resampling = PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips, AudioFileClip, vfx

st.set_page_config(page_title="비요일 제작소 PRO", page_icon="☔")
st.title("☔ 비요일 숏폼 제작소 (최종 안정화 버전)")

def process_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as t:
        t.write(file.read())
        if ext in ['.mp4', '.mov']:
            # 영상은 소리 끄고 가로폭 1080으로 맞춤
            clip = VideoFileClip(t.name).without_audio().resize(width=1080)
        else:
            # 이미지는 9:16 비율(1080x1920)로 강제 조정
            img = PIL.Image.open(t.name).convert("RGB")
            img = img.resize((1080, 1920), PIL.Image.ANTIALIAS)
            img.save(t.name + ".png")
            clip = ImageClip(t.name + ".png").set_duration(2.0)
    return clip.set_fps(24).crossfadein(0.5).crossfadeout(0.5)

files = st.file_uploader("사진이나 영상 클립을 선택하세요", accept_multiple_files=True, type=['jpg','png','mp4','mov'])
logo = st.file_uploader("브랜드 로고를 올려주세요", type=['jpg','png'])
bgm = st.file_uploader("배경음악(MP3) 선택사항", type=['mp3'])

if st.button("✨ 영상 제작 시작"):
    if files and logo:
        with st.spinner('영상을 부드럽게 굽고 있습니다... 잠시만 기다려 주세요.'):
            try:
                # 1. 메인 클립들 처리
                clips = [process_file(f) for f in files]
                
                # 2. 로고 엔딩 (4초, 서서히 확대 효과)
                l_clip = process_file(logo).set_duration(4.0)
                l_clip = l_clip.fx(vfx.resize, lambda t: 1 + 0.02 * t)
                clips.append(l_clip)
                
                # 3. 클립 합치기 (0.5초씩 겹쳐서 부드럽게)
                final = concatenate_videoclips(clips, method="compose", padding=-0.5)
                
                # 4. 음악 입히기
                if bgm:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mt:
                        mt.write(bgm.read())
                        final = final.set_audio(AudioFileClip(mt.name).set_duration(final.duration))
                
                final.write_videofile("biyoil_final.mp4", fps=24, codec="libx264", audio_codec="aac")
                st.video("biyoil_final.mp4")
                st.success("완성! 위 영상에서 우클릭하여 저장하세요.")
            except Exception as e:
                st.error(f"제작 중 에러 발생: {e}")
    else:
        st.error("파일을 모두 올려줘!")
