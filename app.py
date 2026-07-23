import streamlit as st
import PIL.Image
# 최신 버전 에러를 막기 위한 긴급 조치
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, vfx
import tempfile
import os

st.set_page_config(page_title="비요일 제작소", page_icon="☔")
st.title("☔ 비요일 숏폼 자동 제작기 (안정화 버전)")

# 이미지 리사이징 함수 (에러 방지를 위해 moviepy 기능을 안 쓰고 PIL을 직접 사용)
def safe_resize(input_path, output_path):
    with PIL.Image.open(input_path) as img:
        target_w, target_h = 1080, 1920
        img = img.convert("RGB")
        img.thumbnail((target_w, target_h), PIL.Image.Resampling.LANCZOS)
        new_img = PIL.Image.new("RGB", (target_w, target_h), (255, 255, 255))
        new_img.paste(img, ((target_w - img.size[0]) // 2, (target_h - img.size[1]) // 2))
        new_img.save(output_path, "PNG")

images = st.file_uploader("사진들을 선택하세요", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
logo = st.file_uploader("로고를 올려주세요", type=['jpg', 'jpeg', 'png'])
bgm = st.file_uploader("배경음악(MP3) 선택사항", type=['mp3'])

if st.button("✨ 영상 생성 시작"):
    if images and logo:
        with st.spinner('영상을 제작 중입니다...'):
            try:
                clips = []
                # 1. 사진들 처리
                for img_file in images:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_in:
                        tmp_in.write(img_file.read())
                        tmp_out = tmp_in.name + "_done.png"
                        safe_resize(tmp_in.name, tmp_out) # 수동 리사이징
                        clip = ImageClip(tmp_out).set_duration(2.0).set_fps(24).crossfadein(0.5)
                        clips.append(clip)
                
                # 2. 로고 처리
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as l_in:
                    l_in.write(logo.read())
                    l_out = l_in.name + "_logo.png"
                    safe_resize(l_in.name, l_out)
                    logo_clip = ImageClip(l_out).set_duration(4.0).set_fps(24).crossfadein(1.0)
                    # 줌 인 효과
                    logo_clip = logo_clip.fx(vfx.resize, lambda t: 1 + 0.02 * t)
                    clips.append(logo_clip)
                
                # 3. 합치기
                final_video = concatenate_videoclips(clips, method="compose")
                
                if bgm:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as mfile:
                        mfile.write(bgm.read())
                        audio = AudioFileClip(mfile.name).set_duration(final_video.duration)
                        final_video = final_video.set_audio(audio)
                
                out_name = "biyoil_final.mp4"
                final_video.write_videofile(out_name, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(out_name)
                st.success("완성! 위 영상에서 우클릭하여 저장하세요.")
                
            except Exception as e:
                st.error(f"오류: {e}")
    else:
        st.error("파일을 모두 올려주세요.")
