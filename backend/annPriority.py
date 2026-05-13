import math

# HIDDEN LAYER WEIGHTS & BIASES
# Rows  neurons in the hidden layer 4 neurons
# Columns  weights for each of the 4 input features
hiddenWeights = [
    [0.9, 0.8, 0.7, 0.6],   # Neuron 1 — responds strongly to all four signals
    [0.7, 0.9, 0.8, 0.5],   # Neuron 2 — especially sensitive to severity
    [0.6, 0.7, 0.9, 0.8],   # Neuron 3 — especially sensitive to time pressure
    [0.8, 0.6, 0.7, 0.9]    # Neuron 4 — especially sensitive to passenger load
]

# Negative biases push all hidden neurons toward 0 when inputs are weak,
# which makes them "quiet" for ordinary civilian requests.
hiddenBiases = [-0.3, -0.3, -0.3, -0.3]

# OUTPUT LAYER WEIGHTS & BIASES
# Row 0 ,> "Low"      neuron  negative weights , fires when hidden is quiet
# Row 1 ,> "Normal"   neuron  mild positive weights
# Row 2 ,> "High"     neuron  stronger positive weights
# Row 3 ,> "Critical" neuron  very strong positive weights
# The biases here act as thresholds , Critical needs a very loud hidden layer
# to overcome its large negative bias and activate.
outputWeights = [
    [-2.1, -1.9, -2.0, -2.0],   # Low      — inverse of activity
    [ 1.0,  1.1,  0.9,  1.0],   # Normal   — moderate activity
    [ 2.0,  1.8,  2.2,  2.0],   # High     — significant activity
    [ 3.1,  2.9,  3.0,  3.0]    # Critical — maximum activity required
]

outputBiases = [1.5, -1.5, -4.0, -7.5]

def sigmoid(x):
    # Guard against extreme values that would cause math.exp overflow
    if x < -500:
        return 0.0
    if x > 500:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))

def dotProduct(weightRow, inputVector):
    total = 0.0
    for i in range(len(weightRow)):
        total = total + (weightRow[i] * inputVector[i])
    return total

def forwardPass(featureVector):
    # Hidden Layer 
    hiddenActivations = []
    for i in range(4):
        # Weighted sum of all inputs for hidden neuron i, plus its bias
        weightedSum = dotProduct(hiddenWeights[i], featureVector) + hiddenBiases[i]
        hiddenActivations.append(sigmoid(weightedSum))

    # Output Layer 
    outputScores = []
    for i in range(4):
        # Weighted sum of hidden activations for output neuron i, plus its bias
        weightedSum = dotProduct(outputWeights[i], hiddenActivations) + outputBiases[i]
        outputScores.append(sigmoid(weightedSum))

    return outputScores

def predictPriority(featureVector):
    priorityLabels = ["Low", "Normal", "High", "Critical"]

    outputScores = forwardPass(featureVector)

    # Find the index of the highest confidence output neuron
    bestIndex = 0
    for i in range(1, len(outputScores)):
        if outputScores[i] > outputScores[bestIndex]:
            bestIndex = i

    predictedLabel = priorityLabels[bestIndex]
    confidence     = round(outputScores[bestIndex], 4)

    return predictedLabel, confidence
