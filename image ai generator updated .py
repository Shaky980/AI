MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
# If this model fails, try: "black-forest-labs/FLUX.1-schnell"
ENHANCE_SYS = (
    "Improve prompts for text-to-image. Return ONLY the enhanced prompt. "
    "Add subject, style, lighting, camera/angle, background, colors. Keep it safe."
)
NEGATIVE = "nsfw, nude, nudity, naked, erotic, porn, explicit, gore, blood, violence, weapon, hate symbols"
WORDS = [
    "nude","nudity","porn","sex","sexual","explicit","erotic","fetish","nsfw",
    "blood","gore","dismember","decapitate","kill","murder","suicide","self-harm",
    "gun","weapon","knife","bomb","terror","hate","racism","nazi","abuse","drugs","hate speech"
]
PATS = [
    r"\b(nude|nudity|topless|nsfw)\b",
    r"\b(sex|sexual|porn|explicit|erotic|fetish)\b",
    r"\b(gore|blood|dismember|decapitat)\w*\b",
    r"\b(kill|murder|suicide|self[-\s]?harm)\b",
    r"\b(gun|weapon|knife|bomb|explosive)\b",
    r"\b(hate|racis|nazi)\w*\b"
]
def is_safe(p: str):
    p2 = p.lower()
    for w in WORDS:
        if w in p2:
            return False, f"Blocked keyword: {w}"
    for pat in PATS:
        if re.search(pat, p, flags=re.I):
            return False, "Blocked unsafe pattern"
    return True, ""
img_client = InferenceClient(provider="hf-inference", api_key=config.HF_API_KEY)
def enhance_prompt(raw: str) -> str:
    from hf import generate_response
    out = generate_response(f"{ENHANCE_SYS}\nUser prompt: {raw}", temperature=0.4, max_tokens=220)
    return (out or raw).strip()
def gen_image(prompt: str):
    ok, reason = is_safe(prompt)
    if not ok:
        return None, f"⚠️ Prompt contains restricted/unsafe content. {reason}. Please modify and try again."
    try:
        return img_client.text_to_image(prompt=prompt, negative_prompt=NEGATIVE, model=MODEL_ID), None
    except Exception as e:
        msg = str(e)
        if "negative_prompt" in msg or "unexpected keyword" in msg:
            try:
                return img_client.text_to_image(prompt=prompt, model=MODEL_ID), None
            except Exception as e2:
                msg = str(e2)
        if any(x in msg for x in ["402", "Payment Required", "pre-paid credits"]):
            return None, "❌ Image backend requires credits or model not available on hf-inference.\n\nRaw error: " + msg
        if "404" in msg or "Not Found" in msg:
            return None, "❌ Model not served on this provider route (hf-inference).\n\nRaw error: " + msg
        return None, "Error during image generation: " + msg
st.set_page_config(page_title="Safe AI Image Generator", layout="centered")
st.title("🖼️ Safe AI Image Generator (Hugging Face)")
st.info("Flow: You enter a prompt → we enhance it (HF text) → we generate the image (HF Inference).")
with st.form("image_form"):
    raw = st.text_area("Image Description", height=120,
                       placeholder="Example: A cozy cabin in snowy mountains at sunrise, cinematic lighting")
    submit = st.form_submit_button("Generate Image")
if submit:
    if not raw.strip():
        st.warning("⚠️ Please enter an image description.")
    else:
        with st.spinner("Enhancing your prompt..."):
            final_prompt = enhance_prompt(raw.strip())
        ok, reason = is_safe(final_prompt)
        if not ok:
            st.error(f"⚠️ Unsafe enhanced prompt. {reason}. Please rephrase and try again.")
        else:
            st.markdown("#### Enhanced Prompt")
            st.code(final_prompt)
            with st.spinner("Generating image..."):
                img, err = gen_image(final_prompt)
            if err:
                st.error(err)
            else:
                st.image(img, caption="Generated Image", use_container_width=True)
                st.session_state.generated_image = img
img = st.session_state.get("generated_image")
if img:
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button("📥 Download Image", buf.getvalue(), "ai_generated_image.png", "image/png")
if __name__ == "__main__":
    main()
