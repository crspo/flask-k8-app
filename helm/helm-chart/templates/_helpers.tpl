{{- define "yourchart.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "yourchart.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "yourchart.name" .) -}}
{{- end }}

{{- define "yourchart.chart" -}}
{{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

