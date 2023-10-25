from dataclasses import dataclass
from typing import Union, List

from sigma.exceptions import SigmaTransformationError
from sigma.processing.transformations import FieldMappingTransformation, DetectionItemTransformation, Transformation
from sigma.rule import SigmaDetectionItem, SigmaRule


@dataclass
class FieldMappingTransformationLowercase(FieldMappingTransformation):
    """
    Represents a transformation that maps fields using case-insensitive comparison.

    This class extends the basic `FieldMappingTransformation` by allowing field mapping
    to be performed in a case-insensitive manner.

    Methods:
    - get_mapping(field): Fetches the mapped value(s) for a given field considering lowercase
                          comparison of field names.
    """

    def get_mapping(self, field: str) -> Union[None, str, List[str]]:
        """
        Retrieve the mapping for the provided field using case-insensitive comparison.

        The field name is transformed to lowercase before attempting to fetch its mapping.
        This ensures that the field mapping is case-insensitive.

        Parameters:
        - field (str): The field name for which the mapping should be fetched.

        Returns:
        - Union[None, str, List[str]]: Returns the mapped value(s) for the field. It could be None
                                       (if no mapping exists), a string (single mapping), or a list
                                       of strings (multiple mappings).
        """
        return super().get_mapping(field.lower())


@dataclass
class FieldDetectionItemFailureTransformation(DetectionItemTransformation):
    """
    A transformation that raises an error for a specific Sigma detection item.

    When the transformation is applied, it raises a `SigmaTransformationError` with
    a specified error message. This class is intended for situations where a detection
    item is known to be unsupported or problematic and needs to be flagged during
    processing.

    Attributes:
    - message (str): The error message template that will be formatted with the
                     detection item's field and raised as a `SigmaTransformationError`.

    Methods:
    - apply_detection_item: Applies the transformation to a given Sigma detection item.
    """
    message: str

    def apply_detection_item(self, detection_item: SigmaDetectionItem) -> None:
        """
        Applies the transformation to the provided detection item.

        This method raises a `SigmaTransformationError` using the `message` attribute
        formatted with the detection item's field.

        Parameters:
        - detection_item (SigmaDetectionItem): The Sigma detection item to be transformed.

        Raises:
        - SigmaTransformationError: Raised with the formatted message.
        """
        raise SigmaTransformationError(self.message.format(detection_item.field))


class ReferencedFieldTransformation(Transformation):
    def apply(self, pipeline: "sigma.processing.pipeline.Process", rule: SigmaRule) -> None:
        super().apply(pipeline, rule)
        fields: List[str] = []
        for key in pipeline.field_mappings.keys():
            value = pipeline.field_mappings[key]

            # Check if value is of type set
            if not isinstance(value, set):
                raise TypeError(f"Expected a set for key '{key}', but got {type(value).__name__} instead.")

            # Check if set contains exactly one element
            if len(value) != 1:
                raise ValueError(
                    f"Expected a set with exactly one element for key '{key}', but got {len(value)} elements instead.")

            value_str = str(list(value)[0])  # Convert set to list and get the first element
            fields.append(value_str)
        pipeline.state["Fields"] = fields
