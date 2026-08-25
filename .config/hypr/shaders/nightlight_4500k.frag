precision highp float;
varying vec2 v_texcoord;
uniform sampler2D tex;

void main() {
    vec4 pixColor = texture2D(tex, v_texcoord);
    // 4500K Balanced Intermediate Warmth
    pixColor.g = pixColor.g * 0.90;
    pixColor.b = pixColor.b * 0.78;
    gl_FragColor = pixColor;
}
