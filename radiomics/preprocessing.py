import SimpleITK as sitk
import numpy, operator

class RadiomicsHelpers:

  @staticmethod
  def binImage(binwidth, parameterValues, parameterMatrix, parameterMatrixCoordinates):
    lowBound = min(parameterValues) - binwidth
    highBound = max(parameterValues) + binwidth

    binedges = numpy.union1d(numpy.arange(0,lowBound,-binwidth), numpy.arange(0,highBound,binwidth))
    histogram = numpy.histogram(parameterValues, bins=binedges)
    parameterMatrix[parameterMatrixCoordinates] = numpy.digitize(parameterValues,binedges)

    return parameterMatrix, histogram

  @staticmethod
  def imageToNumpyArray(imageFilePath):
    sitkImage = sitk.ReadImage(imageFilePath)
    sitkImageArray = sitk.GetArrayFromImage(sitkImage)
    return sitkImageArray

  @staticmethod
  def padCubicMatrix(a, matrixCoordinates, dims):
    # pads matrix 'a' with zeros and resizes 'a' to a cube with dimensions increased to the next greatest power of 2
    # numpy version 1.7 has numpy.pad function
    # center coordinates onto padded matrix
    # consider padding with NaN or eps = numpy.spacing(1)
    pad = tuple(map(operator.div, tuple(map(operator.sub, dims, a.shape)), ([2,2,2])))
    matrixCoordinatesPadded = tuple(map(operator.add, matrixCoordinates, pad))
    matrix2 = numpy.zeros(dims)
    matrix2[matrixCoordinatesPadded] = a[matrixCoordinates]
    return (matrix2, matrixCoordinatesPadded)

  @staticmethod
  def padTumorMaskToCube(imageNodeArray, labelNodeArray):
    targetVoxelsCoordinates = numpy.where(labelNodeArray != 0)
    ijkMinBounds = numpy.min(targetVoxelsCoordinates, 1)
    ijkMaxBounds = numpy.max(targetVoxelsCoordinates, 1)
    matrix = numpy.zeros(ijkMaxBounds - ijkMinBounds + 1)
    matrixCoordinates = tuple(map(operator.sub, targetVoxelsCoordinates, tuple(ijkMinBounds)))
    matrix[matrixCoordinates] = imageNodeArray[targetVoxelsCoordinates].astype('int64')
    return(matrix, matrixCoordinates)

  @staticmethod
  def interpolateImage(imageNode, resampledPixelSpacing, interpolator=sitk.sitkBSpline):
    """Resamples image or label to the specified pixel spacing (The default interpolator is Bspline)
    
    'imageNode' is a SimpleITK Object, and 'resampledPixelSpacing' is the output pixel spacing. 
    Enumerator references for interpolator:
    0 - sitkNearestNeighbor
    1 - sitkLinear
    2 - sitkBSpline
    3 - sitkGaussian
    """ 
    rif = sitk.ResampleImageFilter()
    rif.SetOutputSpacing(resampledPixelSpacing)
    rif.SetInterpolator(interpolator)
    resampledImageNode = rif.Execute(imageNode)
    return resampledImageNode
