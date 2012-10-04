// Copyright (c) 2012 Thumbtack, Inc.

var Abba = (function(Abba, jStat) {

// Friendly wrapper over jStat's normal distribution functions.
Abba.NormalDistribution = function(mean, standardDeviation) {
    if (mean === undefined) {
        mean = 0;
    }
    if (standardDeviation === undefined) {
        standardDeviation = 1;
    }
    this.mean = mean;
    this.standardDeviation = standardDeviation;
};
Abba.NormalDistribution.prototype = {
    density: function(value) {
        return jStat.normal.pdf(value, this.mean, this.standardDeviation);
    },

    // Returns P(x < value) for x standard normal. value may be any number.
    cdf: function(value) {
        return jStat.normal.cdf(value, this.mean, this.standardDeviation);
    },

    // Returns P(x > value) for x standard normal. value may be any number.
    survival: function(value) {
        return 1 - this.cdf(value);
    },

    // Returns z such that P(x < z) = probability for x standard normal.
    // probability must be in (0, 1).
    inverseCdf: function(probability) {
        return jStat.normal.inv(probability, this.mean, this.standardDeviation);
    },

    // Returns z such that P(x > z) = probability for x standard normal.
    // probability must be in (0, 1).
    inverseSurvival: function(probability) {
        return this.mean - (this.inverseCdf(probability) - this.mean);
    }
};

/* Distribution functions for the binomial distribution. Computes exact binomial results for small
   samples and falls back on the normal approximation for large samples.
*/
Abba.BinomialDistribution = function(numTrials, probability) {
    this.SMALL_SAMPLE_MAX_TRIALS = 100;
    this.numTrials = numTrials;
    this.probability = probability;
    this.expectation = numTrials * probability;
    this.standardDeviation = Math.sqrt(this.expectation * (1 - probability));

    // normal approximation to this binomial distribution
    this._normal = new Abba.NormalDistribution(this.expectation, this.standardDeviation);
    this._lowerTailProbability = this._normal.cdf(-0.5);
    this._upperTailProbability = this._normal.survival(numTrials + 0.5);
};
Abba.BinomialDistribution.prototype = {
    mass: function(count) {
        if (this.numTrials <= this.SMALL_SAMPLE_MAX_TRIALS) {
            return jStat.binomial.pdf(count, this.numTrials, this.probability);
        } else {
            return this._normal.density(count);
        }
    },

    _rescaleProbability: function(probability) {
        return probability / (1 - this._lowerTailProbability - this._upperTailProbability);
    },

    cdf: function(count) {
        if (count < 0) {
            return 0;
        } else if (count >= this.numTrials) {
            return 1;
        } else if (this.numTrials <= this.SMALL_SAMPLE_MAX_TRIALS) {
            return jStat.binomial.cdf(count, this.numTrials, this.probability);
        } else {
            return this._rescaleProbability(
                this._normal.cdf(count + 0.5) - this._lowerTailProbability);
        }
    },

    survival: function(count) {
        return 1 - this.cdf(count);
    },

    inverseCdf: function(probability) {
        return Math.max(0, Math.min(this.numTrials, this._normal.inverseCdf(probability)));
    },

    inverseSurvival: function(probability) {
        return Math.max(0, Math.min(this.numTrials, this._normal.inverseSurvival(probability)));
    }
};

Abba.ValueWithInterval = function(value, lowerBound, upperBound) {
    this.value = value;
    this.lowerBound = lowerBound;
    this.upperBound = upperBound;
}

// A value with standard error, from which a confidence interval can be derived.
Abba.ValueWithError = function(value, error) {
    this.value = value;
    this.error = error;
}
Abba.ValueWithError.prototype = {
    /* criticalZValue should be the value at which the right-tail probability for a standard
       normal distribution equals half the desired alpha = 1 - confidence level:

       P(Z > zValue) = 1 - alpha / 2

       where Z is an N(0, 1) random variable.  Use NormalDistribution.inverseSurvival(), or see
       http://en.wikipedia.org/wiki/Standard_normal_table.
    */
    confidenceIntervalWidth: function(criticalZValue) {
        return criticalZValue * this.error;
    },

    valueWithInterval: function(criticalZValue, estimatedValue) {
        var intervalWidth = this.confidenceIntervalWidth(criticalZValue);
        if (estimatedValue === undefined) {
            estimatedValue = this.value;
        }
        return new Abba.ValueWithInterval(estimatedValue,
                                          this.value - intervalWidth,
                                          this.value + intervalWidth);
    }
};

// Represents a binomial proportion with numSuccesses successful trials out of numTrials total.
Abba.Proportion = function(numSuccesses, numTrials) {
    this.numSuccesses = numSuccesses;
    this.numTrials = numTrials;
    this._binomial = new Abba.BinomialDistribution(numTrials, numSuccesses / numTrials);
}
Abba.Proportion.prototype = {
    /* Compute an estimate of the underlying probability of success.

       Uses the "Agresti-Coull" or "adjusted Wald" interval, which can be thought of as a Wald
       interval with (zCriticalValue^2 / 2) added to the number of successes and the number of
       failures. The estimated probability of success is the center of the interval. This provides
       much better coverage than the Wald interval (and many other intervals), though it has the
       unintuitive property that the estimated probabilty is not numSuccesses / numTrials. See
       (section 1.4.2 and problem 1.24):

       Agresti, Alan. Categorical data analysis. New York, NY: John Wiley & Sons; 2002.

       An ordinary Wald interval can be obtained by passing zCriticalValue = 0.
    */
    pEstimate: function(zCriticalValue) {
        var squaredZCriticalValue = zCriticalValue * zCriticalValue;
        var adjustedNumTrials = this.numTrials + squaredZCriticalValue;
        var adjustedBinomial = new Abba.BinomialDistribution(
            adjustedNumTrials,
            (this.numSuccesses + squaredZCriticalValue / 2) / adjustedNumTrials);
        return new Abba.ValueWithError(
            adjustedBinomial.probability,
            adjustedBinomial.standardDeviation / adjustedBinomial.numTrials);
    }
};

Abba.ProportionComparison = function(baseline, variation) {
    this.baseline = baseline;
    this.variation = variation;
    this._standardNormal = new Abba.NormalDistribution();
}
Abba.ProportionComparison.prototype = {
    // Generate an estimate of the difference in success rates between the variation and the
    // baseline.
    differenceEstimate: function(zCriticalValue) {
        var baselineP = this.baseline.pEstimate(zCriticalValue);
        var variationP = this.variation.pEstimate(zCriticalValue);
        var difference = variationP.value - baselineP.value;
        var standardError = Math.sqrt(Math.pow(baselineP.error, 2) + Math.pow(variationP.error, 2));
        return new Abba.ValueWithError(difference, standardError);
    },

    // Return the difference in sucess rates as a proportion of the baseline success rate.
    differenceRatio: function(zCriticalValue) {
        var baselineValue = this.baseline.pEstimate(zCriticalValue).value;
        var ratio = this.differenceEstimate(zCriticalValue).value / baselineValue;
        var error = this.differenceEstimate(zCriticalValue).error / baselineValue;
        return new Abba.ValueWithError(ratio, error);
    },

    /* For the given binomial distribution, compute an interval that covers at least
       (1 - coverageAlpha) of the total probability mass, centered at the expectation (unless we're
       at the boundary). Uses the normal approximation.
    */
    _binomialCoverageInterval: function(distribution, coverageAlpha) {
        if (distribution.numTrials < 1000) {
            // don't even bother trying to optimize for small-ish sample sizes
            return [0, distribution.numTrials];
        } else {
            return [
                Math.floor(distribution.inverseCdf(coverageAlpha / 2)),
                Math.ceil(distribution.inverseSurvival(coverageAlpha / 2))
            ];
        }
    },

    /* Given the probability of an event, compute the probability that it happens at least once in
       numTests independent tests. This is used to adjust a p-value for multiple comparisons.
       When used to adjust alpha instead, this is called a Sidak correction (the logic is the same,
       the formula is inverted):

       http://en.wikipedia.org/wiki/Bonferroni_correction#.C5.A0id.C3.A1k_correction
    */
    _probabilityUnion: function(probability, numTests) {
        return 1 - Math.pow(1 - probability, numTests);
    },

    /* Compute a p-value testing null hypothesis H0: pBaseline == pVariation against alternative
       hypothesis H1: pBaseline != pVariation by summing p-values conditioned on individual baseline
       success counts. This provides a more accurate correction for multiple testing but scales like
       O(sqrt(this.baseline.numTrials)), so can eventually get slow for very large values.

       Lower coverageAlpha increases accuracy at the cost of longer runtime. Roughly, the result
       will be accurate within no more than coverageAlpha (but this ignores error due to the normal
       approximation so isn't guaranteed).
    */
    iteratedTest: function(numTests, coverageAlpha) {
        var observedAbsoluteDelta = Math.abs(
            this.variation.pEstimate(0).value - this.baseline.pEstimate(0).value);
        if (observedAbsoluteDelta == 0) {
            // a trivial case that the code below does not handle well
            return 1;
        }

        var pooledProportion =
            (this.baseline.numSuccesses + this.variation.numSuccesses)
            / (this.baseline.numTrials + this.variation.numTrials);
        var variationDistribution = new Abba.BinomialDistribution(this.variation.numTrials,
                                                                  pooledProportion);
        var baselineDistribution = new Abba.BinomialDistribution(this.baseline.numTrials,
                                                                 pooledProportion);

        var baselineLimits = this._binomialCoverageInterval(baselineDistribution, coverageAlpha);
        var pValue = 0;
        for (var baselineSuccesses = baselineLimits[0];
             baselineSuccesses <= baselineLimits[1];
             baselineSuccesses++) {
            var baselineProportion = baselineSuccesses / this.baseline.numTrials;
            var lowerTrialCount = Math.floor(
                (baselineProportion - observedAbsoluteDelta) * this.variation.numTrials);
            var upperTrialCount = Math.ceil(
                (baselineProportion + observedAbsoluteDelta) * this.variation.numTrials);
            // p-value of variation success counts "at least as extreme" for this particular
            // baseline success count
            var pValueAtBaseline =
                variationDistribution.cdf(lowerTrialCount)
                + variationDistribution.survival(upperTrialCount - 1);

            // this is exact because we're conditioning on the baseline count, so the multiple
            // tests are independent.
            var adjustedPValue = this._probabilityUnion(pValueAtBaseline, numTests);

            var baselineProbability = baselineDistribution.mass(baselineSuccesses);
            pValue += baselineProbability * adjustedPValue;
        }

        // the remaining baseline values we didn't cover contribute less than coverageAlpha to the
        // sum, so adding that amount gives us a conservative upper bound.
        return pValue + coverageAlpha;
    }
};

// numVariations: number of variations to be compared to the baseline
Abba.Experiment = function(numVariations, baselineNumSuccesses, baselineNumTrials, baseAlpha) {
    this.P_VALUE_PRECISION = 1e-5;

    normal = new Abba.NormalDistribution();
    this._baseline = new Abba.Proportion(baselineNumSuccesses, baselineNumTrials);

    this._numComparisons = Math.max(1, numVariations);
    var alpha = baseAlpha / this._numComparisons // Bonferroni correction
    // all z-values are two-tailed
    this._zCriticalValue = normal.inverseSurvival(alpha / 2);
}
Abba.Experiment.prototype = {
    getBaselineProportion: function() {
        return this._baseline
            .pEstimate(this._zCriticalValue)
            .valueWithInterval(this._zCriticalValue, this._baseline.pEstimate(0).value);
    },

    getResults: function(numSuccesses, numTrials) {
        var trial = new Abba.Proportion(numSuccesses, numTrials);
        var comparison = new Abba.ProportionComparison(this._baseline, trial);
        return {
            proportion: trial
                .pEstimate(this._zCriticalValue)
                .valueWithInterval(this._zCriticalValue, trial.pEstimate(0).value),
            relativeImprovement: comparison
                .differenceRatio(this._zCriticalValue)
                .valueWithInterval(this._zCriticalValue, comparison.differenceRatio(0).value),
            pValue: comparison.iteratedTest(this._numComparisons, this.P_VALUE_PRECISION)
        };
    }
};

return Abba;
}(Abba || {}, jStat));