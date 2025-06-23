import enum


class Annotations(enum, str):
	EnableAnnotationKey = "enable.version-checker.io"
	OverrideURLAnnotationKey = "override-url.version-checker.io"
	UseSHAAnnotationKey = "use-sha.version-checker.io"
	ResolveSHAToTagsKey = "resolve-sha-to-tags.version-checker.io"
	MatchRegexAnnotationKey = "match-regex.version-checker.io"
	UseMetaDataAnnotationKey = "use-metadata.version-checker.io"
	PinMajorAnnotationKey = "pin-major.version-checker.io"
	PinMinorAnnotationKey = "pin-minor.version-checker.io"
	PinPatchAnnotationKey = "pin-patch.version-checker.io"
