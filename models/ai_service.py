import os
import io
import json
import random
from PIL import Image

# Virtual Try-On Import
try:
    from fashn_vton import TryOnPipeline
    HAS_FASHN = True
except ImportError:
    HAS_FASHN = False

# Singleton for the FASHN pipeline to avoid re-loading weights
_pipeline_instance = None


def _get_fashn_pipeline(weights_dir=None):
    global _pipeline_instance
    if not HAS_FASHN:
        return None

    if _pipeline_instance is None:
        if not weights_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            weights_dir = os.path.join(base_dir, 'fashn-vton-1.5', 'weights')

        if not os.path.exists(weights_dir) or not os.path.exists(os.path.join(weights_dir, 'model.safetensors')):
            return None

        try:
            _pipeline_instance = TryOnPipeline(weights_dir=weights_dir)
        except Exception as e:
            print(f"Error loading FASHN pipeline: {e}")
            return None

    return _pipeline_instance


def generate_outfit_image(prompt, product_image_path=None, api_key=None, user_image_path=None, weights_dir=None):
    """
    Generate a virtual try-on image using the local FASHN VTON 1.5 model.
    Requires: user profile photo (person) + product photo (garment).
    Returns: {'success': True, 'image_data': <raw PNG bytes>} or error dict.
    """
    pipeline = _get_fashn_pipeline(weights_dir=weights_dir)

    if not HAS_FASHN:
        return {'success': False, 'error': 'FASHN VTON library not installed. Run: cd fashn-vton-1.5 && pip install -e .'}

    if pipeline is None:
        _wdir = weights_dir or r'T:\fashn-weights'
        return {
            'success': False,
            'error': (
                'Model weights not found. Please run: '
                f'python fashn-vton-1.5/scripts/download_weights.py --weights-dir {_wdir} '
                '(Requires ~2 GB free disk space)'
            )
        }

    if not user_image_path or not os.path.exists(user_image_path):
        return {'success': False, 'error': 'User profile photo is required for virtual try-on. Please upload one in your profile.'}

    if not product_image_path or not os.path.exists(product_image_path):
        return {'success': False, 'error': 'Product image is missing.'}

    try:
        person_img  = Image.open(user_image_path).convert("RGB")
        garment_img = Image.open(product_image_path).convert("RGB")

        # Map product category from prompt text
        category = "tops"
        prompt_lower = (prompt or "").lower()
        if any(x in prompt_lower for x in ['dress', 'jumpsuit', 'gown', 'suit', 'one-piece']):
            category = "one-pieces"
        elif any(x in prompt_lower for x in ['pant', 'skirt', 'short', 'jean', 'trouser', 'bottom']):
            category = "bottoms"

        result = pipeline(
            person_image=person_img,
            garment_image=garment_img,
            category=category,
            num_samples=1,
            num_timesteps=30,
            guidance_scale=1.5,
            seed=42,
            segmentation_free=True
        )

        output_image = result.images[0]
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')

        return {
            'success': True,
            'image_data': img_byte_arr.getvalue(),
            'mime_type': 'image/png'
        }

    except Exception as e:
        return {'success': False, 'error': f"Inference Error: {str(e)}"}


# ─── Rule-Based Style Advisor (replaces external API) ────────────────────────

_BODY_TIPS = {
    'hourglass': (
        "This piece works beautifully with your hourglass figure — it will naturally accentuate your waist and balanced proportions.",
        "Look for styles that hug your curves without being overly tight."
    ),
    'pear': (
        "This garment is a great match for your pear shape — it draws attention upward and balances your silhouette.",
        "Opt for bold tops and darker bottoms to create visual balance."
    ),
    'apple': (
        "This item complements your apple body type well — empire waists and flowing cuts will feel comfortable and flattering.",
        "Choose pieces that flow away from the midsection for a relaxed yet styled look."
    ),
    'rectangle': (
        "This is an excellent pick for your rectangular frame — it adds visual curves and definition where needed.",
        "Layering and textured fabrics work great to add dimension."
    ),
    'inverted_triangle': (
        "This garment suits your inverted triangle shape perfectly — it balances broader shoulders with a flowing lower body.",
        "Wide-leg pants or A-line skirts paired with fitted tops look stunning on you."
    ),
}

_SKIN_COLORS = {
    'fair':   ['navy blue', 'deep burgundy', 'forest green', 'soft lavender'],
    'light':  ['cobalt blue', 'coral', 'teal', 'blush pink'],
    'medium': ['olive green', 'warm orange', 'mustard yellow', 'rust brown'],
    'olive':  ['earth tones', 'burnt sienna', 'camel', 'deep plum'],
    'tan':    ['white', 'bright yellow', 'electric blue', 'hot coral'],
    'dark':   ['bright white', 'royal gold', 'fuchsia', 'vivid orange'],
}

_STYLING_TIPS = {
    'tops': [
        "Pair with high-waisted trousers or tailored chinos for a polished look.",
        "Layer over a fitted turtleneck for added depth in cooler months.",
        "Complete with white sneakers or loafers for casual elegance."
    ],
    'bottoms': [
        "Style with a tucked-in blouse or a structured blazer on top.",
        "A simple monochromatic top will let the bottom piece speak for itself.",
        "Ankle boots or strappy sandals elevate this effortlessly."
    ],
    'one-pieces': [
        "A structured belt at the waist adds instant definition.",
        "Layer with a denim or leather jacket for a more casual vibe.",
        "Block-heeled mules or classic pumps complete this beautifully."
    ],
}

_OCCASION_TIPS = {
    'casual':    "Keep accessories minimal — a simple watch or small hoop earrings work perfectly.",
    'formal':    "Opt for classic accessories: a structured bag, understated jewellery and closed-toe heels.",
    'party':     "Go bold — statement earrings, a clutch, and strappy heels will make you shine.",
    'work':      "Keep it professional: a tailored blazer, neat flats or block heels, and a tote bag.",
    'sports':    "Focus on comfort — breathable socks, supportive sneakers, and a cap if outdoors.",
    'festive':   "Layer on the sparkle — embellished accessories and metallic footwear are your best friends.",
}


def get_style_advice(user_data, product_name, api_key=None, model=None):
    """
    Rule-based personalised styling advice engine.
    No external API required — works 100% offline.
    """
    body_type  = (user_data.get('body_type') or 'rectangle').lower()
    skin_tone  = (user_data.get('skin_tone')  or 'medium').lower()
    occasion   = (user_data.get('occasion')   or 'casual').lower()
    gender     = (user_data.get('gender')     or 'person').lower()
    height     = user_data.get('height', 165) or 165

    # Detect category from product name
    p_lower = product_name.lower()
    if any(x in p_lower for x in ['dress', 'gown', 'jumpsuit', 'saree', 'kurta set']):
        cat = 'one-pieces'
    elif any(x in p_lower for x in ['pant', 'jean', 'trouser', 'skirt', 'short']):
        cat = 'bottoms'
    else:
        cat = 'tops'

    body_lines  = _BODY_TIPS.get(body_type, _BODY_TIPS['rectangle'])
    colors      = _SKIN_COLORS.get(skin_tone, _SKIN_COLORS['medium'])
    style_tips  = _STYLING_TIPS.get(cat, _STYLING_TIPS['tops'])
    occasion_tip = _OCCASION_TIPS.get(occasion, _OCCASION_TIPS['casual'])

    height_note = ""
    if int(height) < 160:
        height_note = " Vertical stripes or monochromatic outfits can elongate your silhouette."
    elif int(height) > 180:
        height_note = " Bold horizontal patterns and colour-blocking work especially well on your tall frame."

    advice = f"""**Why it suits you**
{body_lines[0]}{height_note}
{body_lines[1]}

**How to style it**
• {style_tips[0]}
• {style_tips[1]}
• {style_tips[2]}
• {occasion_tip}

**Colour pairing tips**
Your {skin_tone} skin tone pairs beautifully with {', '.join(colors[:2])}. For contrast and depth, try adding {', '.join(colors[2:])} as accent pieces or accessories."""

    return {'success': True, 'advice': advice}


def analyze_image_with_gemini(image_path, api_key=None, model=None):
    """
    Lightweight pixel-sampler to estimate skin tone and suggest body type.
    Fully offline — no external API required.
    """
    try:
        from PIL import ImageStat
        img = Image.open(image_path).convert("RGB")
        img.thumbnail((200, 200))

        stat = ImageStat.Stat(img)
        r, g, b = stat.mean[:3]
        brightness = (r + g + b) / 3

        if brightness > 210:
            skin_tone = 'fair'
        elif brightness > 185:
            skin_tone = 'light'
        elif brightness > 155:
            skin_tone = 'medium'
        elif brightness > 125:
            skin_tone = 'olive'
        elif brightness > 95:
            skin_tone = 'tan'
        else:
            skin_tone = 'dark'

        # Width/height ratio gives a loose shape hint
        w, h = img.size
        ratio = w / h if h else 1
        if ratio > 0.65:
            body_type = 'rectangle'
        elif ratio > 0.55:
            body_type = 'hourglass'
        else:
            body_type = 'pear'

        return {
            'success': True,
            'data': {
                'body_type': body_type,
                'skin_tone': skin_tone,
                'suggestions': [
                    f"Your {skin_tone} skin tone works great with complementary colour palettes.",
                    f"Your {body_type} body type is well-suited to structured and layered styles.",
                    "Upload a well-lit, front-facing photo for a more accurate reading."
                ]
            }
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}
