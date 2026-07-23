import streamlit as st
import PIL.Image
if not hasattr(PIL.Image, 'Resampling'): # 최신 Pillow 대응
    PIL.Image.Resampling = PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
import tempfile
import os

st.set_page_config(page_title="비요일 PRO", page_icon="☔")
st.title("☔ 비요일 숏폼 제작소 (PRO v3)")

def process_media(file):
    t = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1])
    t.write(file.read())
    if file.name.lower().endswith(('.mp4', '.mov')):
        clip = VideoFileClip(t.name).without_audio().resize(width=1080)
    else:
        with PIL.Image.open(t.name) as img:
            img = img.convert("RGB").resize((1080, 1920), PIL.Image.ANTIALIAS)
            img.save(t.name + ".png")
            clip = ImageClip(t.name + ".png").set_duration(2.0)
    return clip.set_fps(24).crossfadein(0.5).crossfadeout(0.5)

files = st.file_uploader("사진/영상 업로드", accept_multiple_files=True, type=['jpg','png','mp4','mov'])
logo = st.file_uploader("로고 업로드", type=['jpg','png'])
bgm = st.file_uploader("BGM (MP3)", type=['mp3'])

if st.button("✨ 영상 제작 시작"):
    if files and logo:
        with st.spinner('제작 중...'):
            clips = [process_media(f) for f in files]
            l_clip = process_media(logo).set_duration(4.0).fx(vfx.resize, lambda t: 1 + 0.02*t)
            clips.append(l_clip)
            final = concatenate_videoclips(clips, method="compose", padding=-0.5)
            if bgm:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mt:
                    mt.write(bgm.read())
                    final = final.set_audio(AudioFileClip(mt.name).set_duration(final.duration))
            final.write_videofile("out.mp4", fps=24, codec="libx264")
            st.video("out.mp4")
    else: st.error("파일을 올려줘.")
