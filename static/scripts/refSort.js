// Yoinked from https://stackoverflow.com/a/27309301.
function refSort (targetData, refData) {
    // Create an array of indices [0, 1, 2, ...N].
    var indices = Object.keys(refData);
  
    // Sort array of indices according to the reference data.
    indices.sort(function(indexA, indexB) {
      if (refData[indexA] < refData[indexB]) {
        return -1;
      } else if (refData[indexA] > refData[indexB]) {
        return 1;
      }
      return 0;
    });
  
    // Map array of indices to corresponding values of the target array.
    return indices.map(function(index) {
      return targetData[index];
    });
}
