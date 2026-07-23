import streamlit as st
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
import tempfile
import os

st.set_page_config(page_title="비요일 프로 제작소", page_icon="☔")
st.title("☔ 비요일 숏폼 제작소 (PRO 버전)")
st.write("사진과 영상을 섞어서 부드러운 홍보 영상을 만듭니다.")

# 9:16 비율 규격 설정
TARGET_W, TARGET_H = 1080, 1920

def process_source(input_path, is_video=False):
    """이미지와 영상을 9:16 규격으로 통일합니다."""
    if not is_video:
        with PIL.Image.open(input_path) as img:
            img = img.convert("RGB")
            img.thumbnail((TARGET_W, TARGET_H), PIL.Image.Resampling.LANCZOS)
            new_img = PIL.Image.new("RGB", (TARGET_W, TARGET_H), (255, 255, 255))
            new_img.paste(img, ((TARGET_W - img.size[0]) // 2, (TARGET_H - img.size[1]) // 2))
            temp_p = input_path + "_resized.png"
            new_img.save(temp_p, "PNG")
            return ImageClip(temp_p).set_duration(2.0)
    else:
        clip = VideoFileClip(input_path).resize(width=TARGET_W)
        if clip.height > TARGET_H:
            clip = clip.crop(y_center=clip.height/2, height=TARGET_H)
        else:
            clip = clip.margin(top=(TARGET_H-clip.height)//2, bottom=(TARGET_H-clip.height)//2, color=(255,255,255))
        return clip.without_audio()

# 1. 파일 업로드 (영상 확장자 mp4, mov 추가)
uploaded_files = st.file_uploader("사진 또는 영상 클립들을 올려주세요", accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'mp4', 'mov'])
logo_file = st.file_uploader("브랜드 로고를 올려주세요", type=['jpg', 'jpeg', 'png'])
bgm_file = st.file_uploader("배경음악(MP3) 선택사항", type=['mp3'])

if st.button("✨ 고퀄리티 영상 생성 시작"):
    if uploaded_files and logo_file:
        with st.spinner('부드러운 전환 효과를 적용 중입니다...'):
            try:
                main_clips = []
                
                # 1. 메인 소스 처리
                for f in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
                        tmp.write(f.read())
                        is_vid = f.name.lower().endswith(('.mp4', '.mov'))
                        clip = process_source(tmp.name, is_video=is_vid)
                        # 부드러운 전환을 위해 모든 클립에 0.5초 페이드 적용
                        clip = clip.crossfadein(0.5).crossfadeout(0.5)
                        main_clips.append(clip)
                
                # 2. 로고 엔딩 처리 (블랙 화면 방지를 위해 패딩 없이 바로 연결)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as l_tmp:
                    l_tmp.write(logo_file.read())
                    logo_clip = process_source(l_tmp.name, is_video=False).set_duration(4.0)
                    logo_clip = logo_clip.fx(vfx.resize, lambda t: 1 + 0.02 * t) # 줌 인 무빙
                    logo_clip = logo_clip.crossfadein(0.5)
                    main_clips.append(logo_clip)
                
                # 3. 합치기 (padding=-0.5를 주어 앞뒤 클립이 겹치며 부드럽게 전환되게 함)
                final_video = concatenate_videoclips(main_clips, method="compose", padding=-0.5)
                
                # 4. 음악 입히기
                if bgm_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as m_tmp:
                        m_tmp.write(bgm_file.read())
                        audio = AudioFileClip(m_tmp.name).set_duration(final_video.duration)
                        final_video = final_video.set_audio(audio)
                
                output_path = "biyoil_pro_final.mp4"
                final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_path)
                st.success("🎉 업그레이드된 영상이 완성되었습니다!")
                
            except Exception as e:
                st.error(f"제작 중 오류 발생: {e}")
    else:
        st.error("소스 파일과 로고를 모두 등록해주세요.")
