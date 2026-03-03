"""
Style Mate - Rule-Based Expert System for Outfit Recommendations
"""

# Body type recommendations
BODY_TYPE_RULES = {
    'hourglass': {
        'recommended_styles': ['wrap dresses', 'fitted blazers', 'high-waist pants', 'bodycon', 'belted outfits'],
        'avoid': ['boxy tops', 'shapeless dresses'],
        'description': 'Balanced proportions - celebrate your curves!'
    },
    'pear': {
        'recommended_styles': ['A-line skirts', 'bootcut jeans', 'off-shoulder tops', 'wide-leg pants', 'empire waist'],
        'avoid': ['skinny jeans', 'pencil skirts', 'low-rise bottoms'],
        'description': 'Fuller hips - draw attention to your upper body!'
    },
    'apple': {
        'recommended_styles': ['empire waist', 'flowy tops', 'straight-leg pants', 'V-necks', 'maxi dresses'],
        'avoid': ['tight tops', 'high-waist bottoms', 'cropped jackets'],
        'description': 'Fuller midsection - elongate your silhouette!'
    },
    'rectangle': {
        'recommended_styles': ['peplum tops', 'ruffles', 'belted dresses', 'flared skirts', 'layered looks'],
        'avoid': ['straight-cut dresses', 'boxy shapes'],
        'description': 'Balanced frame - add curves and definition!'
    },
    'inverted_triangle': {
        'recommended_styles': ['A-line skirts', 'wide-leg pants', 'flared jeans', 'dark tops', 'V-necks'],
        'avoid': ['boat necks', 'cap sleeves', 'shoulder pads'],
        'description': 'Broad shoulders - balance with fuller bottoms!'
    }
}

# Skin tone color recommendations
SKIN_TONE_RULES = {
    'fair': {
        'best_colors': ['navy', 'burgundy', 'forest green', 'blush pink', 'lavender', 'deep purple'],
        'avoid_colors': ['neon', 'very pale yellow', 'white-on-white'],
        'neutrals': ['charcoal', 'light grey', 'cream']
    },
    'light': {
        'best_colors': ['coral', 'teal', 'blue', 'peach', 'soft rose', 'sage green'],
        'avoid_colors': ['very pale colors that wash out'],
        'neutrals': ['beige', 'ivory', 'light grey']
    },
    'medium': {
        'best_colors': ['olive', 'mustard', 'terracotta', 'warm red', 'royal blue', 'emerald'],
        'avoid_colors': ['very pastel shades'],
        'neutrals': ['camel', 'tan', 'warm white']
    },
    'olive': {
        'best_colors': ['purple', 'magenta', 'bright blue', 'coral', 'gold', 'bright green'],
        'avoid_colors': ['yellow-green', 'orange'],
        'neutrals': ['white', 'black', 'navy']
    },
    'tan': {
        'best_colors': ['orange', 'bright yellow', 'electric blue', 'hot pink', 'turquoise'],
        'avoid_colors': ['beige', 'brown tones similar to skin'],
        'neutrals': ['white', 'cream', 'black']
    },
    'dark': {
        'best_colors': ['bright white', 'vivid yellow', 'bold red', 'electric blue', 'neon green', 'gold'],
        'avoid_colors': ['very dark shades without contrast'],
        'neutrals': ['white', 'ivory', 'bright grey']
    }
}

# Occasion recommendations
OCCASION_RULES = {
    'casual': {
        'styles': ['jeans', 't-shirts', 'casual dresses', 'joggers', 'polo shirts', 'sneakers'],
        'fabrics': ['cotton', 'denim', 'jersey', 'linen'],
        'formality': 'relaxed'
    },
    'formal': {
        'styles': ['suits', 'blazers', 'dress pants', 'formal dresses', 'button-down shirts', 'pencil skirts'],
        'fabrics': ['wool', 'silk', 'polyester blend', 'crepe'],
        'formality': 'professional'
    },
    'party': {
        'styles': ['cocktail dresses', 'dressy separates', 'sequined outfits', 'party jumpsuits', 'statement pieces'],
        'fabrics': ['sequin', 'satin', 'velvet', 'lace'],
        'formality': 'festive'
    },
    'wedding': {
        'styles': ['sarees', 'lehengas', 'anarkalis', 'sherwanis', 'suits', 'gowns'],
        'fabrics': ['silk', 'chiffon', 'georgette', 'brocade'],
        'formality': 'traditional/formal'
    },
    'sports': {
        'styles': ['activewear', 'track pants', 'sports bras', 'shorts', 'athletic tops'],
        'fabrics': ['polyester', 'spandex', 'moisture-wicking fabric'],
        'formality': 'athletic'
    },
    'office': {
        'styles': ['formal trousers', 'blazers', 'formal shirts', 'midi dresses', 'pencil skirts'],
        'fabrics': ['cotton blend', 'polyester', 'crepe', 'wool'],
        'formality': 'business casual to formal'
    },
    'beach': {
        'styles': ['swimwear', 'flowy cover-ups', 'linen shorts', 'sundresses', 'sarongs'],
        'fabrics': ['linen', 'cotton', 'jersey', 'swimwear fabric'],
        'formality': 'relaxed'
    }
}

# Climate recommendations
CLIMATE_RULES = {
    'hot': {
        'fabrics': ['cotton', 'linen', 'chambray', 'rayon'],
        'styles': ['light colors', 'loose fitting', 'short sleeves', 'breathable'],
        'avoid': ['heavy fabrics', 'dark colors that absorb heat', 'tight fits']
    },
    'cold': {
        'fabrics': ['wool', 'cashmere', 'fleece', 'velvet', 'denim'],
        'styles': ['layering', 'full sleeves', 'turtlenecks', 'coats', 'dark colors'],
        'avoid': ['thin fabrics', 'bare skin styles']
    },
    'moderate': {
        'fabrics': ['cotton blend', 'polyester', 'silk', 'jersey'],
        'styles': ['versatile layering', 'medium weight fabrics', 'neutral colors'],
        'avoid': ['very heavy or very light extremes']
    },
    'rainy': {
        'fabrics': ['synthetic', 'quick-dry', 'waterproof outer layers'],
        'styles': ['darker colors', 'waterproof jackets', 'quick-dry fabrics'],
        'avoid': ['white', 'light colors', 'non-waterproof materials']
    },
    'humid': {
        'fabrics': ['cotton', 'linen', 'moisture-wicking'],
        'styles': ['loose fitting', 'light colors', 'breathable fabrics'],
        'avoid': ['synthetic non-breathable fabrics', 'tight fits']
    }
}

# BMI and size recommendations
def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (cm)"""
    if height and weight and height > 0:
        height_m = height / 100
        return round(weight / (height_m ** 2), 1)
    return None

def get_size_recommendation(height, weight, chest=None, waist=None, hips=None, gender='unisex'):
    """Determine clothing size based on measurements"""
    sizes = []
    
    if gender == 'female' and chest and waist and hips:
        if chest <= 82 and waist <= 62 and hips <= 88:
            sizes.append('XS')
        elif chest <= 87 and waist <= 67 and hips <= 93:
            sizes.append('S')
        elif chest <= 92 and waist <= 72 and hips <= 98:
            sizes.append('M')
        elif chest <= 97 and waist <= 77 and hips <= 103:
            sizes.append('L')
        elif chest <= 102 and waist <= 82 and hips <= 108:
            sizes.append('XL')
        else:
            sizes.append('XXL')
    elif gender == 'male' and chest and waist:
        if chest <= 88 and waist <= 73:
            sizes.append('XS')
        elif chest <= 93 and waist <= 78:
            sizes.append('S')
        elif chest <= 98 and waist <= 83:
            sizes.append('M')
        elif chest <= 103 and waist <= 88:
            sizes.append('L')
        elif chest <= 108 and waist <= 93:
            sizes.append('XL')
        else:
            sizes.append('XXL')
    else:
        # Size by weight
        if weight:
            if weight < 50:
                sizes.append('XS')
            elif weight < 60:
                sizes.append('S')
            elif weight < 72:
                sizes.append('M')
            elif weight < 85:
                sizes.append('L')
            elif weight < 100:
                sizes.append('XL')
            else:
                sizes.append('XXL')
    
    return sizes[0] if sizes else 'M'

def get_outfit_recommendations(user_data):
    """
    Main rule-based recommendation engine.
    Returns a dictionary with recommendations.
    """
    recommendations = {
        'body_type_tips': [],
        'color_palette': [],
        'occasion_styles': [],
        'climate_tips': [],
        'size': 'M',
        'bmi': None,
        'bmi_category': '',
        'filters': {}
    }
    
    gender = user_data.get('gender', 'unisex')
    body_type = user_data.get('body_type', '').lower().replace(' ', '_')
    skin_tone = user_data.get('skin_tone', '').lower()
    occasion = user_data.get('occasion', '').lower()
    climate = user_data.get('climate', '').lower()
    height = user_data.get('height')
    weight = user_data.get('weight')
    chest = user_data.get('chest')
    waist = user_data.get('waist')
    hips = user_data.get('hips')
    budget = user_data.get('budget')
    
    # BMI Calculation
    if height and weight:
        bmi = calculate_bmi(float(weight), float(height))
        recommendations['bmi'] = bmi
        if bmi:
            if bmi < 18.5:
                recommendations['bmi_category'] = 'Underweight'
            elif bmi < 25:
                recommendations['bmi_category'] = 'Normal'
            elif bmi < 30:
                recommendations['bmi_category'] = 'Overweight'
            else:
                recommendations['bmi_category'] = 'Obese'
    
    # Size Recommendation
    recommendations['size'] = get_size_recommendation(
        height, weight, chest, waist, hips, gender
    )
    
    # Body Type Tips
    if body_type in BODY_TYPE_RULES:
        body_rules = BODY_TYPE_RULES[body_type]
        recommendations['body_type_tips'] = body_rules['recommended_styles']
        recommendations['body_type_description'] = body_rules['description']
    
    # Color Palette (Skin Tone Based)
    if skin_tone in SKIN_TONE_RULES:
        tone_rules = SKIN_TONE_RULES[skin_tone]
        recommendations['color_palette'] = tone_rules['best_colors']
        recommendations['avoid_colors'] = tone_rules['avoid_colors']
        recommendations['neutral_colors'] = tone_rules['neutrals']
    
    # Occasion Styles
    if occasion in OCCASION_RULES:
        occ_rules = OCCASION_RULES[occasion]
        recommendations['occasion_styles'] = occ_rules['styles']
        recommendations['occasion_fabrics'] = occ_rules['fabrics']
        recommendations['formality'] = occ_rules['formality']
    
    # Climate Tips
    if climate in CLIMATE_RULES:
        cli_rules = CLIMATE_RULES[climate]
        recommendations['climate_tips'] = cli_rules['styles']
        recommendations['climate_fabrics'] = cli_rules['fabrics']
    
    # Build filter dict for product filtering
    recommendations['filters'] = {
        'gender': gender,
        'occasion': occasion,
        'climate': climate,
        'body_type': body_type,
        'skin_tone': skin_tone,
        'budget': budget,
        'size': recommendations['size']
    }
    
    return recommendations

def build_outfit_prompt(user_data, product_data, recommendations):
    """Build a detailed AI image generation prompt."""
    gender = user_data.get('gender', 'person')
    body_type = user_data.get('body_type', '')
    skin_tone = user_data.get('skin_tone', '')
    height = user_data.get('height', '')
    occasion = user_data.get('occasion', '')
    climate = user_data.get('climate', '')
    
    product_name = product_data.get('name', 'outfit')
    product_color = product_data.get('color', '')
    product_category = product_data.get('category', '')
    
    color_palette = ', '.join(recommendations.get('color_palette', [])[:3])
    
    prompt = f"""Create a professional fashion visualization image showing a {gender} model wearing {product_name}.

Model characteristics:
- Gender: {gender}
- Body type: {body_type}
- Skin tone: {skin_tone}
- Height: {height}cm

Outfit details:
- Item: {product_name}
- Color: {product_color}
- Category: {product_category}
- Occasion: {occasion}
- Climate: {climate}

Style requirements:
- Show the complete outfit on the model in a professional fashion photography style
- Use complementary colors: {color_palette}
- High quality, magazine-style photography
- Clean white or gradient background
- Full body or 3/4 view showing the outfit clearly
- Professional lighting that highlights fabric texture and fit
- The model should appear natural and confident
- Include styling accessories appropriate for {occasion} occasion

Make this look like a premium fashion e-commerce product visualization."""

    return prompt
