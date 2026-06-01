shader_type spatial;


uniform sampler2D albedo;

void fragment() {
	vec3 texture_image = texture(albedo, UV).rgb;
	ALBEDO = vec3(floor(UV.x * 10.0) / 10.0, 0.0, 0.0);
}
