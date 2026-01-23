---
name: generate
description: Nano Banana Pro (nano-banana-pro) image generation skill. Use this skill when the user asks to "generate an image", "generate images", "create an image", "make an image", uses "nano banana", or requests multiple images like "generate 5 images". Generates images using Google's Gemini 2.5 Flash for any purpose - frontend designs, web projects, illustrations, graphics, hero images, icons, backgrounds, or standalone artwork. Invoke this skill for ANY image generation request.
---

# Nano Banana Pro - Gemini Image Generation

Generate custom images using Google's Gemini models for integration into frontend designs.

## Prerequisites

Set the `GEMINI_API_KEY` environment variable with your Google AI API key.

## Available Models

| Model | ID | Best For | Max Resolution |
|-------|-----|----------|----------------|
| **Flash** | `gemini-2.5-flash-image` | Speed, high-volume tasks | 1024px |
| **Pro** | `gemini-3-pro-image-preview` | Professional quality, complex scenes | Up to 4K |

## Image Generation Workflow

### Step 1: Generate the Image

Use `scripts/image.py` with uv. The script is located in the skill directory at `skills/generate/scripts/image.py`:

```bash
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Your image description" \
  --output "/path/to/output.png"
```

Where `${SKILL_DIR}` is the directory containing this SKILL.md file.

Options:
- `--prompt` (required): Detailed description of the image to generate or edit instruction
- `--output` (required): Output file path (PNG format)
- `--aspect` (optional): Aspect ratio (default: square)
  - **Aliases**: `square` (1:1), `landscape` (16:9), `portrait` (9:16), `wide` (21:9), `photo` (4:3), `photo-portrait` (3:4)
  - **Direct ratios**: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`
- `--reference` (optional): Path to a reference image (can be used multiple times, max 14 images)
- `--edit` (optional): Path to an image to edit (enables edit mode instead of generation)
- `--model` (optional): Model to use - "flash" (fast) or "pro" (high-quality) (default: flash)
- `--size` (optional): Image resolution for pro model - "1K", "2K", "4K" (default: 1K, ignored for flash)

### Using Different Models

**Flash model (default)** - Fast generation, good for iterations:
```bash
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "A minimalist logo design" \
  --output "/path/to/logo.png" \
  --model flash
```

**Pro model** - Higher quality for final assets:
```bash
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "A detailed hero illustration for a tech landing page" \
  --output "/path/to/hero.png" \
  --model pro \
  --size 2K
```

### Using Different Aspect Ratios

**Wide banner (21:9)** - Ultra-wide for hero sections:
```bash
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Abstract gradient waves for website header" \
  --output "/path/to/banner.png" \
  --aspect wide
```

**Social media post (4:5)** - Instagram-style vertical:
```bash
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Product showcase with clean background" \
  --output "/path/to/post.png" \
  --aspect 4:5
```

**Photo format (4:3)** - Traditional camera ratio:
```bash
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Landscape photography style scene" \
  --output "/path/to/photo.png" \
  --aspect photo
```

### Using Reference Images

Use one or more reference images for style, composition, or content guidance:

**Single reference image:**
```bash
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Create a similar abstract pattern with warmer colors" \
  --output "/path/to/output.png" \
  --reference "/path/to/reference.png"
```

**Multiple reference images (up to 14):**
```bash
# 여러 사람을 조합한 단체 사진
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "A group photo of these people at a party" \
  --output "/path/to/group.png" \
  --reference "/path/to/person1.png" \
  --reference "/path/to/person2.png" \
  --reference "/path/to/person3.png"

# 여러 스타일 블렌딩
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Blend these artistic styles into a landscape" \
  --output "/path/to/blended.png" \
  --reference "/path/to/style1.png" \
  --reference "/path/to/style2.png"

# 캐릭터 일관성 유지
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "The same character in a different pose, standing on a mountain" \
  --output "/path/to/character.png" \
  --reference "/path/to/char_ref1.png" \
  --reference "/path/to/char_ref2.png"
```

Reference images help Gemini understand:
- **Style**: artistic style, color palette, mood
- **Composition**: layout, framing, perspective
- **Subjects**: people, objects, characters to include
- **Character consistency**: maintain same person/character across images

### Editing an Existing Image

Use `--edit` to modify an existing image with natural language instructions:

```bash
# 배경 흐리게
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Blur the background" \
  --output "/path/to/blurred.png" \
  --edit "/path/to/original.png"

# 스타일 변환
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Convert to cartoon style" \
  --output "/path/to/cartoon.png" \
  --edit "/path/to/photo.png"

# 색상 변경
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Change the red elements to blue" \
  --output "/path/to/recolored.png" \
  --edit "/path/to/image.png"

# 객체 제거
uv run "${SKILL_DIR}/scripts/image.py" \
  --prompt "Remove the person in the background" \
  --output "/path/to/cleaned.png" \
  --edit "/path/to/photo.png"
```

Edit mode supports various transformations:
- **Style transfer**: cartoon, oil painting, sketch, etc.
- **Color adjustments**: change colors, add warmth/coolness
- **Background modifications**: blur, remove, replace
- **Object manipulation**: remove, add, move elements
- **Enhancement**: sharpen, denoise, upscale appearance

### Step 2: Integrate with Frontend Design

After generating images, incorporate them into frontend code:

**HTML/CSS:**
```html
<img src="./generated-hero.png" alt="Description" class="hero-image" />
```

**React:**
```jsx
import heroImage from './assets/generated-hero.png';
<img src={heroImage} alt="Description" className="hero-image" />
```

**CSS Background:**
```css
.hero-section {
  background-image: url('./generated-hero.png');
  background-size: cover;
  background-position: center;
}
```

## Crafting Effective Prompts

Write detailed, specific prompts for best results:

**Good prompt:**
> A minimalist geometric pattern with overlapping translucent circles in coral, teal, and gold on a deep navy background, suitable for a modern fintech landing page hero section

**Avoid vague prompts:**
> A nice background image

### Prompt Elements to Include

1. **Subject**: What the image depicts
2. **Style**: Artistic style (minimalist, abstract, photorealistic, illustrated)
3. **Colors**: Specific color palette matching the design system
4. **Mood**: Atmosphere (professional, playful, elegant, bold)
5. **Context**: How it will be used (hero image, icon, texture, illustration)
6. **Technical**: Aspect ratio needs, transparency requirements

## Integration with Frontend-Design Skill

When used alongside the frontend-design skill:

1. **Plan the visual hierarchy** - Identify where generated images add value
2. **Match the aesthetic** - Ensure prompts align with the chosen design direction (brutalist, minimalist, maximalist, etc.)
3. **Generate images first** - Create visual assets before coding the frontend
4. **Reference in code** - Use relative paths to generated images in your HTML/CSS/React

### Example Workflow

1. User requests a landing page with custom hero imagery
2. Invoke nano-banana-pro to generate the hero image with a prompt matching the design aesthetic
3. Invoke frontend-design to build the page, referencing the generated image
4. Result: A cohesive design with custom AI-generated visuals

## Output Location

By default, save generated images to the project's assets directory:
- `./assets/` for simple HTML projects
- `./src/assets/` or `./public/` for React/Vue projects
- Use descriptive filenames: `hero-abstract-gradient.png`, `icon-user-avatar.png`
