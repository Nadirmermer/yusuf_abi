# Confidence Intervals

- **Kaynak Platform**: Simply Psychology
- **Orijinal URL**: https://www.simplypsychology.org/confidence-interval.html
- **Yayın Tarihi**: 2026-09-17T10:58:43+00:00
- **Okuma Süresi / Kelime**: ~13 dk (2596 kelime)
- **Çekilme Zamanı**: 2026-09-22T12:18:12.776640

---

## 📌 Giriş / Özet
Psychology»Statistics


## 🎯 Ana Maddeler & Odak Noktaları (Carousel / Post Çekirdeği)
1. 1. Sample Size (n)
2. 2. Variation in the Data
3. 3. Confidence Level


## 🖼️ Konuyla İlgili Görseller (Arka Plan & Tasarım İçin)
- ![Confidence Intervals](https://www.simplypsychology.org/wp-content/uploads/confidence-interval.jpg) - *Header Image*
- ![95% Confidence Interval Explained](/wp-content/uploads/confidence-interval.jpg)
- ![Why is Z 1.96 at 95 confidence?](/wp-content/uploads/NormalDist1.96.png)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/p-value-300x225.jpeg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/z-score-300x169.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/cohen-d-300x142.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/bell-curve-300x250.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/type-1-and-2-errors-300x222.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/box-whisker-plot-300x165.jpg)
- ![Confidence Interval Formula](/wp-content/uploads/ci-for-the-mean-formula.png)
- ![Confidence Intervals Presented Graphically as High-Low-Close Charts](/wp-content/uploads/confidence-interval2.gif)
- ![apa style table](/wp-content/uploads/apa-table.png)
- ![Statistical significance in ab testing. Where the confidence interval is 95%, the p-value is 0.05](https://www.simplypsychology.org/wp-content/uploads/confidence-interval-1-1024x666.jpeg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/saul-mcleod.jpg)


## 📝 Makale Bölümleri ve Detaylı İçerik

### Giriş

Psychology»Statistics

[preferred_source_button]

The confidence interval (CI) is a range of values that’s likely to include a population value with a certain degree of confidence. It is often expressed as a % whereby a population mean lies between an upper and lower interval.

### Key Takeaways

- Definition:A confidence interval is a range of plausible values for a population parameter, built around a sample estimate at a stated confidence level, usually 95%.

- Not a Probability:Once calculated, an interval either contains the true value or it doesn’t. The “95%” describes how often the procedure succeeds across repeated samples, not this interval’s odds.

- Interval Width:A wider interval comes from a smaller sample, more variable data, or a higher confidence level; a narrower one comes from the opposite.

- APA Reporting:Report a CI in square brackets after the point estimate, e.g.M= 5.50, 95% CI [4.25, 6.75], with no equals sign before the bracket.

- Common Misreading:Confusing “95% confidence” with the odds for one interval is a persistent misreading in the literature (Greenland et al., 2016; Morey et al., 2016).

- 95% CI Explained

- How to Calculate

- Example Calculation

- Interpreting a Confidence Interval

- APA Reporting

- Practice Problems

### Why use confidence intervals?

A confidence interval (CI) is a range of values that likely contains a true population mean. It works like a “safety net” built around a sample result to account for uncertainty.

No single sample is perfect.

A bare percentage or mean, reported alone, hides how much uncertainty surrounds it. Reporting a range instead lets readers judge whether two results are meaningfully different (Wilkinson & the Task Force on Statistical Inference, 1999).

Because researchers rarely test everyone in a population, they rely on a representative sample instead, so the sample mean is rarely exactly the true population mean.

To address this, we create a range of values. This range gives us a more realistic picture of where the actual population average likely sits.

### What is a 95% confidence interval?

A 95% confidence interval (CI) is a statement about thereliability of a statistical procedurerather than a probability for a specific calculated range.

In frequentist statistics, the true population parameter is fixed. It is the interval that varies from sample to sample (Neyman, 1937).

A specific interval does not have a 95% probability of containing the true value: the population value is fixed, so the interval either captures it or it doesn’t.

Instead, “95%” is the method’s long-term success rate.

If you were to repeat an experiment infinitely and calculate an interval each time, approximately 95% of those various intervals would capture the true population parameter.

See this on anormal distributiongraph.

The normal distribution is a symmetrical, bell-shaped curve where most data points sit near the middle. According to the Central Limit Theorem, averages from large samples always form this shape.

This shape is remarkably reliable.

This lets researchers predict how much samples will vary. To build the interval, they first find the standard error (SE), which measures how much a sample mean typically differs from the true mean.

A smaller SE means the sample is a more accurate reflection of the group. To reach 95% confidence, the SE is multiplied by a critical value: the number of standard errors needed for that confidence level, 1.96 in this case.

### Common mistakes to avoid

CIs describe a procedure, not a specific result.

This is one of the most persistent misreadings in the statistical literature. Greenland et al. (2016) catalogued it among 25 documented misinterpretations of p-values, confidence intervals, and statistical power.

Morey et al. (2016) show formally that only a Bayesian credible interval, built from different assumptions, actually answers the “95% probability” question readers instinctively ask.

- Not a Null Test: A CI is not a direct statement about the likelihood of a null hypothesis being true.

- No “95% Probability”: Once calculated, the true mean is either inside or it isn’t; it is incorrect to assign it a probability.

- Not a Data Spread: CIs estimate the population mean, not the range of individual sample scores.

- Not a Predictor: It does not mean 95% of future experiment results will fall into that specific interval.

Correct Definition: If we repeated the experiment over and over, 95% of the resulting intervals would contain the true mean.

### Confidence interval formula

- X(Sample Mean):The average value calculated from the collected data

- Z(Z-score):A standardized value reflecting the chosen confidence level, such as 1.96 for 95%.

- s(Standard Deviation):A measure of the amount of variation or dispersion in the data set

- n(Sample Size):The total number of individual observations or participants included in the sample

The plus and minus symbols indicate the calculation of both an upper and lower limit.

Subtracting the margin of error establishes the lower bound. Adding it creates the upper bound.

These two points define the span of the confidence interval.

### Step 1: Gather Your Initial Information

Before starting your calculations, you need to identify four key pieces of information from your data:

- Sample Mean (x̄):The average value calculated from your sample.

- Sample Size (n):The total number of items or participants in your sample.

- Standard Deviation:Use the population standard deviation (σ) if it is known. If it is unknown, use thestandard error(sample standard deviation).

- Confidence Level (CL):How sure you want to be that the interval contains the true mean (most commonly95%).

### Step 2: Find the Critical Value

Remember, you must calculate an upper and low score for the confidence interval using thez-scorefor the chosen confidence level (see table below).

The critical value depends on your chosen confidence level and whether you know the population standard deviation.

- If σ is known (use z-score):For a 95% confidence level, the criticalz-scoreis1.96.

- If σ is unknown (use t-score):You must use the Student’s t-distribution. You will need yourDegrees of Freedom (df), which isn – 1. You can find the t-score in a t-table or using a calculator.

### Step 3: Calculate the Error Bound (Margin of Error)

The Error Bound for a Population Mean (EBM) tells you how far the true mean is likely to be from your sample mean.

- Formula when σ is known:EBM = z * (σ / sqrt(n))

- Formula when σ is unknown:EBM = t * (s / sqrt(n))

### Step 4: Construct the Interval

To find your final range, subtract the EBM from the sample mean for the lower bound and add it for the upper bound.

- Lower Limit:x̄ – EBM

- Upper Limit:x̄ + EBM

Final Result Format:(Lower Limit, Upper Limit)

### Example Calculation

Suppose a researcher wants to estimate the mean score on a statistics exam.

They take a random sample of 36 scores and find a sample mean of 68. It is known that the population standard deviation (σ) is 3 points.

### Step 1: Identify Your Key Statistics

- Sample Mean (x̄)= 68

- Sample Size (n)= 36

- Population Standard Deviation (σ)= 3

- Confidence Level (CL)= 95% (0.95)

### Step 2: Choose the Distribution

Because the population standard deviation (σ) isknown, we use theNormal (z) Distribution.

### Step 3: Determine the Critical Value

For a95% confidence level, the area in the tails (α) is 0.05 (1 – 0.95). This area is split between two tails, leaving 0.025 in each.

- The criticalz-scorefor 95% confidence is1.96.

### Step 4: Calculate the Margin of Error (EBM)

Using the formula:EBM = z * (σ / sqrt(n))

- Find the square root of n:sqrt(36) = 6

- Divide σ by the result:3 / 6 = 0.5

- Multiply by the z-score:1.96 * 0.5 = 0.98

- Margin of Error (EBM) = 0.98

### Step 5: Construct the Interval

- Lower Bound:x̄ - EBM=68 - 0.98 = 67.02

- Upper Bound:x̄ + EBM=68 + 0.98 = 68.98

Final Result Format: (67.02, 68.98)

### Step 6: Interpretation

“We estimate with 95% confidence that the true population mean statistics exam score is between 67.02 and 68.98”.

### Interpreting a Confidence Interval

We can be confident that the population mean is similar to the sample mean when the confidence interval is narrow.

The narrower the interval (upper and lower values), the more precise our estimate is.

As a general rule, as the sample size increases, the confidence interval should become more narrow.

A narrow interval, typically achieved through a large sample size and low data variability, indicates that the sample mean is likely very close to the true population mean.

### What Dynamics Affect the Width of the Interval?

The width of a 95% confidence interval is determined by themargin of error, which is influenced by three primary factors:

### 1. Sample Size (n)

As the sample size increases, the width of the interval decreases.

Larger samples reduce uncertainty and provide more evidence, which “shrinks” the interval around the point estimate.

- Larger Samples:Asnincreases, the standard error of the mean decreases. This results in a narrower interval, which indicates a more precise estimate of the population mean.

- Smaller Samples:These have higher sampling variability, leading to wider intervals and less certainty that the sample mean is close to the true population mean.

### 2. Variation in the Data

The width of the interval is also directly related to thevariability(standard deviation) of the measure being studied:

- High Variability:If data points are widely spread, the interval must be wider to capture the true mean with the same level of confidence.

- Low Variability:If the data is concentrated closely around the mean, the resulting confidence interval will be narrower.

### 3. Confidence Level

The margin of error also changes based on how much “confidence” you require.

- Increasing Confidence (e.g., 99%):To be more certain the interval captures the true parameter, you must include more of the sampling distribution, which makes the intervalwider.

- Decreasing Confidence (e.g., 90%):This requires a smaller critical value, making the intervalnarrowerbut increasing the risk that it misses the true value.

### How to Report a Confidence Interval (APA Style)

APA style requires you to usesquare bracketsto enclose the confidence limits. You should also clearly state the confidence level (usually 95%).

Standard Template:M= 5.50, 95% CI [4.25, 6.75]

### Key Formatting Rules:

- Abbreviation:You can use “CI” after you have defined it once in the text, or just use it directly if it’s inside parentheses.

- No “to” or dashes:Use a comma to separate the upper and lower limits.

- Consistency:Use the same number of decimal places for the limits as you did for the point estimate.

While it’s common to see people write “95% CI = [4.25, 6.75]”, the APA manual actually prefers that youdon’tuse an equals sign before the brackets. Just a space and the brackets will do!

- For Correlations:r= .35, 95% CI [.15, .52]

- For Regression:B= 1.20, 95% CI [0.95, 1.45]

- For Proportions:60%, 95% CI [55%, 65%]

### Reporting in Different Contexts

How you report the CI depends on where it sits in your sentence.

If the entire statistic is already in parentheses, do not use nested parentheses. Use commas to separate the statistics.

- Example:The effect was significant (d= 0.45, 95% CI [0.12, 0.78]).

If you are discussing the results in a sentence, you can be a bit more descriptive.

- Example:The mean score was 25.4, 95% CI [22.1, 28.7], suggesting a moderate increase.

When reporting multiple CIs in a table, you can use a dedicated column labeled “95% CI” and put the limits in brackets.

### Further Information

- Hypothesis testing and p-values (Khan Academy)

- Publication manual of the American Psychological Association

- Statistics for Psychology Book Download

### Is The confidence interval the same as standard deviation?

No, they’re different. The standard deviation shows how much individual measurements in a group vary from the average. Think of it like how much students’ grades differ from the class average.

A confidence interval, on the other hand, is a range that we’re pretty sure (like 95% sure) contains the true average grade for all classes, based on our class. It’s about our certainty in estimating a true average, not about individual differences.

### Does a boxplot show confidence intervals?

A standardbox plotdisplays medians and interquartile ranges, not confidence intervals. However, some enhanced box plots can include confidence intervals around the median or mean, represented by notches or error bars.

While not a traditional feature, adding confidence intervals can give more insight into the data’s reliability of central tendency estimates.

### Confidence Interval Practice Problems

- A researcher took a sample of 30 students’ test scores with an average score of 85 and a standard deviation of 5. What is the 95% confidence interval for the test scores?

- A study measures the heights of 50 people, finding an average height of 170 cm with a standard deviation of 10 cm. What is the 99% confidence interval for the population’s height?

- In a sample of 40 light bulbs, the mean lifetime is 5000 hours and the standard deviation is 400 hours. Compute a 90% confidence interval for the average lifetime of the bulbs.

### Answers:

- For a 95% confidence interval and a sample size > 30, we typically use a z-score of 1.96. The formula for a confidence interval is (mean – (z* (std_dev/sqrt(n)), mean + (z* (std_dev/sqrt(n)). So, the confidence interval is (85 – (1.96*(5/sqrt(30))), 85 + (1.96*(5/sqrt(30))) = (83.21, 86.79).

- For a 99% confidence interval and a sample size > 30, we typically use a z-score of 2.58. So, the confidence interval is (170 – (2.58*(10/sqrt(50))), 170 + (2.58*(10/sqrt(50))) = (167.35, 172.65).

- For a 90% confidence interval and a sample size > 30, we typically use a z-score of 1.645. So, the confidence interval is (5000 – (1.645*(400/sqrt(40))), 5000 + (1.645*(400/sqrt(40))) = (4870.92, 5129.08).

McLeod, S. (2026). Confidence Intervals. Simply Psychology. https://www.simplypsychology.org/confidence-interval.html

McLeod, Saul. "Confidence Intervals." Simply Psychology, 17 September 2026, https://www.simplypsychology.org/confidence-interval.html.

McLeod, S. (2026) Confidence Intervals. Simply Psychology. Available at: https://www.simplypsychology.org/confidence-interval.html (Accessed: 22 September 2026).

### References

Greenland, S., Senn, S. J., Rothman, K. J., Carlin, J. B., Poole, C., Goodman, S. N., & Altman, D. G. (2016). Statistical tests, P values, confidence intervals, and power: A guide to misinterpretations.European Journal of Epidemiology, 31(4), 337–350. https://doi.org/10.1007/s10654-016-0149-3

Morey, R. D., Hoekstra, R., Rouder, J. N., Lee, M. D., & Wagenmakers, E.-J. (2016). The fallacy of placing confidence in confidence intervals.Psychonomic Bulletin & Review, 23(1), 103–123. https://doi.org/10.3758/s13423-015-0947-8

Neyman, J. (1937). Outline of a theory of statistical estimation based on the classical theory of probability.Philosophical Transactions of the Royal Society of London. Series A, 236(767), 333–380. https://doi.org/10.1098/rsta.1937.0005

Wilkinson, L., & the Task Force on Statistical Inference. (1999). Statistical methods in psychology journals: Guidelines and explanations.American Psychologist, 54(8), 594–604. https://doi.org/10.1037/0003-066X.54.8.594

BSc (Hons) Psychology, MRes, PhD, University of Manchester

Chartered Psychologist (CPsychol)

Saul McLeod, PhD, is a qualified psychology teacher with over 18 years of experience in further and higher education. He has been published in peer-reviewed journals, including the Journal of Clinical Psychology.
