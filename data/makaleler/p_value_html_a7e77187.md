# P-Value Significance

- **Kaynak Platform**: Simply Psychology
- **Orijinal URL**: https://www.simplypsychology.org/p-value.html
- **Yayın Tarihi**: 2026-09-18T11:22:57+00:00
- **Okuma Süresi / Kelime**: ~30 dk (5953 kelime)
- **Çekilme Zamanı**: 2026-09-22T12:26:39.471363

---

## 📌 Giriş / Özet
Psychology»Statistics


## 🎯 Ana Maddeler & Odak Noktaları (Carousel / Post Çekirdeği)
1. The Estimation Approach: “The New Statistics”


## 🖼️ Konuyla İlgili Görseller (Arka Plan & Tasarım İçin)
- ![P-Value Significance](https://www.simplypsychology.org/wp-content/uploads/p-value.jpeg) - *Header Image*
- ![P-Value Explained in Normal Distribution](/wp-content/uploads/p-value.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/type-1-and-2-errors-300x222.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/cohen-d-300x142.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/confidence-interval-300x178.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/z-score-300x169.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/moderating-variable-300x169.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/mediator-moderator-variable-300x169.jpg)
- ![Probability and statistical significance in ab testing. Statistical significance in a b experiments](https://www.simplypsychology.org/wp-content/uploads/p-value-1024x768.jpeg)
- ![statistical significance two tailed](https://www.simplypsychology.org/wp-content/uploads/statistical-significance-two-tailed-1024x666.jpeg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/Olivia-Guy-Evans-1.jpg)
- ![Görsel](https://www.simplypsychology.org/wp-content/uploads/saul-mcleod.jpg)


## 📝 Makale Bölümleri ve Detaylı İçerik

### Giriş

Psychology»Statistics

The p-value in statistics measures how strongly the data contradicts thenull hypothesis.

A smaller p-value means the results are less consistent with the null and may support the alternative hypothesis. Common cutoffs for statistical significance are 0.05 and 0.01.

### Key Takeaways

- Definition:A p-value measures how likely your observed results (or more extreme ones) would be if the null hypothesis were true. It is a tool for assessing evidence against the null.

- Significance:Statistical significance is determined by comparing the p-value to a chosen cutoff (often 0.05). A smaller p-value suggests stronger evidence against the null hypothesis.

- Misinterpretation:A p-value does not tell you the probability the null hypothesis is true or that your results happened by chance. It only reflects how your data aligns with the null model.

- Limitations:A statistically significant result may have little practical importance, and large samples can produce small p-values even for trivial effects. Always consider effect size (how big the difference or relationship actually is) alongside the p-value.

- Best practice:Interpret p-values alongside confidence intervals, study design, and replication evidence to form a more reliable conclusion about your findings.

### Hypothesis testing

When conducting a statistical test, the p-value helps determine whether your results are significant in relation to the null hypothesis.

Thenull hypothesis(H₀)states that no relationship exists between thevariables being studied. Under the null, any difference is attributed to chance, not to the factor you are investigating.

Thealternative hypothesis(H₁ or Hₐ)is the logical opposite. It claims the independent variabledoesinfluence the dependent variable.

Researchers never set out to prove H₁ directly. Instead, they try to reject H₀ — if it is rejected, H₁ becomes the more plausible explanation by elimination, followingKarl Popper’s principle of falsification.

For example, a memory researcher might predict that matching the smell at learning and recall will boost how many words people recall. The null hypothesis, H₀, states that a smell match makes no difference; any change in recall is down to chance.

### What a p-value tells you

A p-value, or probability value, is a number describing how likely it is that your data would have occurred by random chance, if the null hypothesis were true.

It comes from a test statistic. Every test — t, F, chi-squared, and the rest — compares how much variance your effect explains against how much is left unexplained.

A bigger ratio means less room for chance. Because statisticians know how often a given test statistic would occur under the null, that ratio converts directly into the p-value.

The smaller thep-value, the less likely the results occurred by random chance, and the stronger the evidence that you should reject the null hypothesis. It is evidence, not proof.

Remember, a p-value doesn’t tell you if the null hypothesis is true or false. It just tells you how likely you’d see the data you observed, or more extreme data, if the null hypothesis was true.

It can never reach exactly zero. There is always some small possibility that an observed pattern occurred by chance, however unlikely that seems.

Suppose you test whether a new drug provides more pain relief than a placebo.

- If the drug has no real effect, your test statistic will be close to what’s expected under the null hypothesis, and the p-value will be high (close to 1).

- If the drug truly works, your test statistic will differ more from the null expectation, and the p-value will drop.

If the drug has no real effect, your test statistic will be close to what’s expected under the null hypothesis, and the p-value will be high (close to 1).

If the drug truly works, your test statistic will differ more from the null expectation, and the p-value will drop.

A p-value never reaches exactly zero — there’s always a small possibility, however unlikely, that your observed results occurred by chance.

### How to Choose an Alpha Level (significance threshold)

Your chosen alpha level (α) is the cutoff you use to decide whether results are statistically significant. The choice depends on your research context, goals, and the consequences of making a mistake.

- Standard Alpha (α = .05):The most common threshold. Accepts a 5% chance of wrongly finding an effect that doesn’t exist (Type I error). Suitable for most exploratory or general research.

- Stricter Alpha (α = .01 or .001):Used for high-stakes research, like clinical trials, mental health interventions, or policy decisions, where mistakes have serious consequences. A lower alpha reduces the chance of false positives (finding something significant that isn’t actually there).

- Study Size and Reliability:Larger studies (typically 200 or more participants) often let you safely use a stricter alpha (e.g., α = .01), because larger samples provide more reliable results.

- Practical Implications:If making a wrong decision could have major consequences (like health or safety risks), choose a lower alpha to minimize mistakes.

Standard Alpha (α = .05):The most common threshold. Accepts a 5% chance of wrongly finding an effect that doesn’t exist (Type I error). Suitable for most exploratory or general research.

Stricter Alpha (α = .01 or .001):Used for high-stakes research, like clinical trials, mental health interventions, or policy decisions, where mistakes have serious consequences. A lower alpha reduces the chance of false positives (finding something significant that isn’t actually there).

Study Size and Reliability:Larger studies (typically 200 or more participants) often let you safely use a stricter alpha (e.g., α = .01), because larger samples provide more reliable results.

Practical Implications:If making a wrong decision could have major consequences (like health or safety risks), choose a lower alpha to minimize mistakes.

Always state and justify your chosen alpha level to increase transparency and trustworthiness.

### P-value interpretation

The alpha level is a fixed threshold you set in advance; the p-value is calculated from your data. Comparing them tells you whether to reject the null hypothesis:

A p-value at or below a predetermined significance level, often 0.05 or 0.01, counts as statistically significant. This means the data provide strong evidence against the null hypothesis. That’s the threshold.

This suggests the effect under study likely represents a real relationship rather than just random chance.

For instance, if you set α = 0.05, you would reject the null hypothesis if yourp-value ≤ 0.05.

It indicates strong evidence against the null. That does not mean there is a 5% probability the null hypothesis is true. A p-value only tells you how likely the data would be if the null were true, not the reverse.

The null hypothesis is rejected. H₁ becomes the more plausible explanation — not because it has been proven, but because H₀ has been ruled out.

Upon analyzing the pain relief effects of the new drug compared to the placebo, the computed p-value is less than 0.01, which falls well below the predetermined alpha value of 0.05.

Consequently, you conclude that there is a statistically significant difference in pain relief between the new drug and the placebo.

A p-value of 0.001 is highly statistically significant, well beyond the standard 0.05 threshold. It indicates strong evidence of a real effect, not just random variation.

Specifically, it means there is only a 0.1% chance of a result this extreme if the null hypothesis were true. That is rare.

Such a small p-value provides strong evidence against the null hypothesis, favoring the alternative.

This means you fail to reject the null hypothesis. Failing to reject is not the same as proving it true. You can only reject the null hypothesis or fail to reject it, never accept it outright.

Note: when the p-valueis above your threshold of significance,it does not mean that there is a 95% probability that the alternative hypothesis is true.

### One-Tailed Test

In anormal distribution, the significance level corresponds to extreme regions — ortails— of the curve.

The whole 5% sits in one tail.

With α = 0.05, you would reject the null hypothesis if your result falls in the extreme 5% region at one end of the distribution. That end is the right tail for a predicted increase, or the left tail for a predicted decrease.

If it falls there, H₀ is rejected.

In this example, the result is statistically significant, so H₀ is rejected. H₁ becomes the more plausible explanation.

### Two-Tailed Test

Two-tailed tests are used when an effect could occur in either direction. They are the more conservative choice.

α is split equally between both ends of the distribution — 2.5% in each tail, with α = 0.05.

A result has to land further into the extreme to count as significant than a one-tailed test would require.

The choice matters statistically, not just in wording. A one-tailed test at the .05 level is checked against a different, less strict critical value than a two-tailed test at the same nominal level.

Choosing a one-tailed test only after seeing which way the data point is a form of p-hacking. It quietly halves the true significance threshold being applied.

### Type I and Type II Errors

- Type I Error (False Positive):This occurs when you incorrectly find an effect or difference that doesn’t really exist. For instance, concluding a medication improves symptoms when it actually does not. With an alpha (α) level of .05, there’s a 5% chance of making this error.

- Type II Error (False Negative):This happens when you fail to detect an effect that genuinely exists. For example, concluding a medication doesn’t help when it truly does. You can reduce this error by increasing your sample size or improving your research design.

Type I Error (False Positive):This occurs when you incorrectly find an effect or difference that doesn’t really exist. For instance, concluding a medication improves symptoms when it actually does not. With an alpha (α) level of .05, there’s a 5% chance of making this error.

Type II Error (False Negative):This happens when you fail to detect an effect that genuinely exists. For example, concluding a medication doesn’t help when it truly does. You can reduce this error by increasing your sample size or improving your research design.

Reducing a Type II error means increasingstatistical power: the probability a study correctly detects a real effect, calculated as 1 minus the Type II error rate.

The two error types trade off against each other. Lowering the alpha level (say, from .05 to .01) cuts the risk of a Type I error. But a stricter threshold makes a real effect harder to detect, which raises the risk of a Type II error.

The trade-off never fully disappears. Researchers conventionally aim for at least 80% power (Cohen, 1988, 1992). Power, sample size, effect size, and alpha are all linked, so fixing any three lets you calculate the fourth.

### How do you calculate thep-value?

Most statistical software packages like R, SPSS, and others automatically calculate your p-value. This is the easiest and most common way.

You can also estimate a p-value using online calculators or statistical tables, which require your test statistic and degrees of freedom.

These tables show how often you’d expect to see your test statistic if the null hypothesis were true.

Choosing the right test depends on three things. Design (independent groups or repeated measures), level of measurement (nominal, ordinal, interval or ratio), and whether your data are normally distributed.

Tests split into two families. Parametric tests, like the t-test, use the sample mean and standard deviation directly, so they assume a normal distribution. Non-parametric tests, like Mann-Whitney U or chi-squared, convert scores to ranks instead and make no such assumption.

Parametric tests are more powerful. They catch a genuine difference more often for the same sample size. But the gap is smaller than expected.

A non-parametric test ranks scores instead of using the mean and standard deviation. Even so, it detects a real difference nearly as well as its parametric equivalent, in about 95% of cases.

### Understanding the Statistical Test:

Choosing the right statistical test matters because each has its own purpose and assumptions:

- T-test: Compares the means of two groups (e.g., testing if one medication is more effective than another).

- ANOVA(Analysis of Variance). Compares means across three or more groups (e.g., therapy, medication, and combined treatment).

- Chi-squared test: Suitable for categorical data (e.g., evaluating the relationship between smoking status and lung disease).

- Correlation test:Measures the strength and direction of relationships between two continuous variables (e.g., height and weight).

T-test: Compares the means of two groups (e.g., testing if one medication is more effective than another).

ANOVA(Analysis of Variance). Compares means across three or more groups (e.g., therapy, medication, and combined treatment).

Chi-squared test: Suitable for categorical data (e.g., evaluating the relationship between smoking status and lung disease).

Correlation test:Measures the strength and direction of relationships between two continuous variables (e.g., height and weight).

The more variables you include, the more careful you must be interpreting your p-values.

More variables can affect your test statistic, potentially leading to misleading significance.

If you’re comparing the effectiveness of just two different drugs in pain relief, a two-sample t-test is a suitable choice for comparing these two groups. However, when you’re examining the impact of three or more drugs, it’s more appropriate to employ an Analysis of Variance (ANOVA).

Utilizing multiple pairwise comparisons in such cases can lead to artificially low p-values and an overestimation of the significance of differences between the drug groups.

### How to report

A statistically significant result cannot prove that a research hypothesis is correct (which implies 100% certainty).

Instead, we may state our results “provide support for” or “give evidence for” our research hypothesis. There is still a slight probability that the results occurred by chance and the null hypothesis was correct — for example, less than 5%.

In our comparison of pain relief between the new drug and a placebo, participants in the drug group reported significantly lower pain scores (M = 3.5, SD = 0.8) than those in the placebo group (M = 5.2, SD = 0.7). This 1.7-point difference on the pain scale was statistically significant,t(98) = -9.36,p< .001.

### APA Style

The 6th edition of the APA style manual (American Psychological Association, 2010) states the following on the topic of reporting p-values.

“When reportingpvalues, report exactpvalues (e.g., p = .031) to two or three decimal places. However, reportpvalues less than .001 asp< .001.

The tradition of reportingpvalues in the formp< .10,p< .05, p < .01, and so forth, was appropriate in a time when only limited tables of critical values were available.” (p. 114)

- Do not use 0 before the decimal point for the statistical valuepas it cannot equal 1. In other words, writep= .001 instead ofp= 0.001.

- Please pay attention to issues of italics (pis always italicized) and spacing (either side of the = sign).

- p= .000 (as outputted by some statistical packages such as SPSS) is impossible and should be written asp< .001.

- The opposite of significant is “nonsignificant,” not “insignificant.”

### Statistical vs. practical significance

A common mistake is to assume that a lower p-value means a stronger relationship or a more important finding.

In reality, a p-value only tells you how unlikely your data would be if the null hypothesis were true. It does not reveal the size or real-world importance of the effect.

- Statistical significancemeans the evidence is strong enough to reject the null hypothesis at a chosen threshold (e.g.,p< 0.05).

- Practical significance, on the other hand, considers whether the effect is big enough to make a real difference in everyday life, not just in a statistical test.

This is often measured witheffect size, which quantifies the magnitude of the difference or relationship.

### Relationship Between Effect Size, Confidence Intervals, and P-Values

Effect size, confidence intervals, and p-values each contribute uniquely and complementarily to statistical interpretation:

- Effect Size: Measures how large or meaningful the effect is. For example, a therapy may significantly reduce anxiety scores, but if the change is only 1–2 points on a 50-point scale, the practical impact is minimal.

- Confidence Intervals (CIs): Give a range of values in which the true effect likely lies (often 95% CIs). Narrow intervals suggest more precise estimates; wide intervals indicate greater uncertainty.

- P-Values: Reflect statistical significance, not practical value.For example, a very small p-value (such as 0.001) in a depression intervention trial suggests strong statistical evidence that the intervention had some effect, but without effect size, it doesn’t indicate if the change is clinically meaningful.

Effect Size: Measures how large or meaningful the effect is. For example, a therapy may significantly reduce anxiety scores, but if the change is only 1–2 points on a 50-point scale, the practical impact is minimal.

Confidence Intervals (CIs): Give a range of values in which the true effect likely lies (often 95% CIs). Narrow intervals suggest more precise estimates; wide intervals indicate greater uncertainty.

P-Values: Reflect statistical significance, not practical value.

For example, a very small p-value (such as 0.001) in a depression intervention trial suggests strong statistical evidence that the intervention had some effect, but without effect size, it doesn’t indicate if the change is clinically meaningful.

- Small p-value + Large effect size + Narrow CI: Strong evidence that the effect is real and practically significant.

- Small p-value + Small effect size: Indicates statistical significance, but the practical impact may be limited.

- Significant p-value + Wide CI: Suggests uncertainty about the exact size of the effect, indicating caution in interpreting results.

Reporting effect sizes, confidence intervals, and p-values together ensures thorough, transparent, and meaningful interpretation of your research findings.

### Multiple comparisons & p-hacking

When researchers run many statistical tests on the same dataset, the chance of finding a “significant” result purely by luck increases.

This is called themultiple comparisons problem. More tests raise the chance of a false “significant” result.

For example, if you test 20 unrelated hypotheses at the usual α = 0.05 threshold, you can expect about one false positive result just by chance.

P-hackinghappens when researchers — intentionally or not — run many analyses, report only the significant results, or stop collecting data once they get the outcome they want.

This can make an effect seem real when it’s actually just a statistical fluke.

Simmons, Nelson, and Simonsohn (2011) showed exactly this. Combining a handful of ordinary, seemingly innocuous choices, like when to stop collecting data or which measures to report, does real damage. In their simulations, it pushed the true false-positive rate for a nominal 5% test above 60%.

Their own experiments made the point vividly. Using exactly this kind of flexible, undisclosed analysis, they “showed” that listening to a song about growing older made participants younger. The result, reported as a genuine finding, was known in advance to be false.

The point was not that the claim was true. It was that ordinary analytic flexibility can manufacture significance for a hypothesis that plainly is not.

### To avoid these pitfalls, researchers can:

- Pre-registertheir hypotheses and analysis plans before collecting data.

- Useadjustments for multiple testing, such as the Bonferroni correction (dividing your alpha level by the number of comparisons made), to keep the overall error rate under control.

- Reportallanalyses conducted, not just the ones that turned out significant.

Pre-registertheir hypotheses and analysis plans before collecting data.

Useadjustments for multiple testing, such as the Bonferroni correction (dividing your alpha level by the number of comparisons made), to keep the overall error rate under control.

Reportallanalyses conducted, not just the ones that turned out significant.

Statistical significance is most trustworthy when the analysis plan is transparent, focused on the main research questions, and adjusted for the number of tests performed.

### Real-World Applications of Significance Testing

Significance testing shapes decisions well beyond the classroom. Three fields lean on it especially heavily:

- Clinical and health research:A stricter alpha guards against approving an ineffective or unsafe treatment.

- Education:An underpowered study risks a Type II error that buries a genuinely useful teaching method.

- Workplace and organisational psychology:Small, non-randomised samples make power and effect size especially important.

### Clinical and Health Research

The stakes here are real. Drug trials and public-health interventions carry the biggest share of them. Regulators typically require a stricter alpha, often p < .01, before approving a new medication.

A false positive, a Type I error, could put patients on a treatment that does not work. That risk is not hypothetical. It could also expose people to side effects for no real benefit.

A false negative is just as costly. It could withhold a genuinely effective treatment from people who need it.

These are not abstract categories: they decide which drugs and psychological therapies reach the public at all. So much rides on the decision that many trials are structured asrandomized controlled trials, which randomly assign patients specifically to keep the comparison fair.

### Education

Teaching methods live or die by this test. Decisions about which curricula or classroom technologies get adopted often rest on a significance test.

An underpowered study risks a Type II error that quietly buries a genuinely useful method. The risk is not just academic. A virtual-reality teaching approach might truly help students learn.

Education research typically works with modest sample sizes and small-to-moderate effects. The sample size matters most. But if the sample is too small, or the outcome measure too blunt, the study fails to detect the improvement.

That is why funders increasingly expect a stated power analysis before a trial is approved.

Without one, a genuinely better method can go unnoticed for years, and schools may keep a less effective status quo running long after it should have changed.

### Workplace and Organisational Psychology

Staffing numbers are usually the limit here.

Evaluating a training programme or a wellbeing initiative means comparing outcomes like productivity or engagement. The comparison runs before and after a change, or between a trained and an untrained group.

Organisations rarely randomise large numbers of staff. That leaves sample sizes often small. It makes power and effect-size reporting especially important for telling a genuinely useful change from ordinary noise.

Small samples hide real effects. A small, well-powered pilot beats a large, underpowered rollout every time. The maths is no different in a boardroom than in a lab.

The logic scales up cleanly. A change that looks like nothing in a small sample can still be the real thing. Dismissing it as noise, rather than checking whether the study simply lacked the power to see it, is the more common mistake.

### Critical Evaluation

The 0.05 threshold decides “significant” from “not significant.” It is a historical convention, not a mathematical law, and treating it as a hard line carries real costs.

### The 5% Cutoff Is a Convention, Not a Law

Fisher (1925) introduced the 0.05 threshold as a flexible rule of thumb, tied to the era’s printed tables of critical values. He never intended it as a fixed cut-off.

That convention has a real cost. A result of p = .049 gets treated as a genuine discovery, while p = .051 counts as a non-finding — even though the two are barely different.

The American Statistical Association later made the same point: a scientific conclusion should never rest on whether a p-value crosses a single line (Wasserstein & Lazar, 2016). Reducing a nuanced result to a bare “significant” or “not significant” label throws away information a continuous p-value actually carries.

The lesson is not that p-values are useless. It is that the threshold deserves less weight than it has traditionally carried.

### Bayesian Statistics: A Different Question

A p-value answers one specific question: how likely is this data, assuming the null hypothesis is true? Bayesian statistics asks something different — how likely is the hypothesis, given this data?

Bayesian methods update a starting probability into a revised one using the observed evidence (Dienes, 2011). This is called a posterior probability. They can also do something NHST cannot: distinguish real evidence for the null hypothesis from data that is simply inconclusive.

There is a catch. A Bayesian analysis requires specifying a starting probability in advance, and how that choice is made can itself become a source of disagreement.

Both approaches answer real, useful questions about the same data. Which one to use depends on what you actually want to know, and on how comfortable you are stating a prior.

### The Estimation Approach: “The New Statistics”

A third approach argues for moving away from null hypothesis significance testing (NHST) altogether, not just supplementing it. Instead of a reject/retain decision, it puts point estimates, confidence intervals, and meta-analytic thinking at the centre of every result (Cumming, 2014).

The logic is simple. On this view, a confidence interval already shows what a bare p-value hides: direction and size. A literature built from accumulating effect-size estimates is more cumulative than one built from individual accept/reject decisions.

It is also less exposed to a false significant/non-significant split. Cumming (2014) does not dismiss the p-value outright.

He argues instead that the estimate, not the p-value, should be the headline result. Treating the p-value as one supporting detail leaves a field less exposed to p-hacking and all-or-nothing thinking.

### Contemporary Research

Aim:The Open Science Collaboration (2015) set out to directly test how often published, statistically significant psychology findings actually replicate.

Method:More than 270 researchers selected 100 studies from three top psychology journals and ran high-powered replication attempts of each one, using the original materials and procedures where possible.

Results:Almost all the original studies were significant. That held for 97% of them, using the standard p < .05 cutoff. Only 36% of the direct replications did, and the effect that did replicate was about half the original size.

Conclusion:Many findings did not replicate. The field had overestimated how often real effects exist, and how large they are.

Not every methodologist agrees. Gilbert, King, Pettigrew, and Wilson (2016) argued that several replication attempts differed from the originals in ways that could explain non-replication without the original findings being false positives.

The pattern is not unique to psychology.

Camerer et al. (2018) replicated 21 social-science experiments originally published inNatureandSciencebetween 2010 and 2015, and found that only 13 of the 21 (62%) replicated successfully. Their replication effect sizes again averaged around half the size of the originals.

That is not a coincidence. Together, the two projects suggest the pattern uncovered by the Open Science Collaboration is not an artefact of the three journals it happened to sample. It looks like a more general feature of how significance-based publishing incentives work across the social sciences.

### When do you reject the null hypothesis?

In statistical hypothesis testing, you reject the null hypothesis when the p-value is less than or equal to the significance level (α) you set before conducting your test.

The significance level is the probability of rejecting the null hypothesis when it is true. Commonly used significance levels are 0.01, 0.05, and 0.10.

Remember, rejecting the null hypothesis doesn’t prove the alternative hypothesis; it just suggests that the alternative hypothesis may be plausible given the observed data.

Thep-value is conditional upon the null hypothesis being true but is unrelated to the truth or falsity of the alternative hypothesis.

### What does p-value of 0.05 mean?

If your p-value is less than or equal to 0.05 (the significance level), you would conclude that your result is statistically significant.

This means the evidence is strong enough to reject the null hypothesis in favor of the alternative hypothesis.

### Are all p-values below 0.05 considered statistically significant?

No, not all p-values below 0.05 are considered statistically significant. The threshold of 0.05 is commonly used, but it’s just a convention.

Statistical significance depends on factors like the study design, sample size, and the magnitude of the observed effect.

A p-value below 0.05 means there is evidence against the null hypothesis, suggesting a real effect. However, it’s essential to consider the context and other factors when interpreting results.

Researchers also look at effect size and confidence intervals to determine the practical significance and reliability of findings.

### How does sample size affect the interpretation of p-values?

Sample size can impact the interpretation of p-values. A larger sample size provides more reliable and precise estimates of the population, leading to narrower confidence intervals.

With a larger sample, even small differences between groups or effects can become statistically significant, yielding lower p-values.

In contrast, smaller sample sizes may not have enough statistical power to detect smaller effects, resulting in higher p-values.

Therefore, a larger sample size increases the chances of finding statistically significant results when there is a genuine effect, making the findings more trustworthy and robust.

### Can a non-significant p-value indicate that there is no effect or difference in the data?

No, a non-significant p-value does not necessarily indicate that there is no effect or difference in the data. It means that the observed data do not provide strong enough evidence to reject the null hypothesis.

There could still be a real effect or difference, but it might be smaller or more variable than the study was able to detect.

Other factors like sample size, study design, and measurement precision can influence the p-value. It’s important to consider the entire body of evidence and not rely solely on p-values when interpreting research findings.

### Can P values be exactly zero?

While a p-value can be extremely small, it cannot technically be absolute zero.

When a p-value is reported asp= 0.000, the actual p-value is too small for the software to display. This is often interpreted as strong evidence against the null hypothesis. For p values less than 0.001, report asp< .001

### My experiment yielded a p-value of 0.06. Should I discard my hypothesis entirely? How should I interpret this result accurately?

A p-value of 0.06 means there’s only a 6% chance your results would occur if there’s truly no effect—still relatively low.

Being close to significance might suggest there could be an effect, but your evidence isn’t strong enough yet.

You might have encountered a Type II error (failing to detect a real effect).

If your sample size is small or your study has low statistical power (below 80%), you may have missed detecting an actual effect.

Look at the effect size: is it meaningful enough to matter in real-world scenarios?

A practically significant effect could still be important, even without statistical significance.

If your confidence interval is narrow and mostly suggests a meaningful effect, this increases confidence that the result may still have practical value.

A wide interval suggests greater uncertainty, making conclusions less reliable.

Assess if there were methodological limitations or biases (like measurement error or uncontrolled variables) that may have weakened your results.

Check if other research supports similar findings or trends. If consistent with existing literature, your result could still be meaningful.

### Can p-values be manipulated or misleading?

Yes. P-values can be misleading if researchers engage in practices likep-hacking– repeating analyses, selectively reporting results, or stopping data collection once significance is reached.

They can also appear small in very large samples even for trivial effects, so context and additional statistics are essential.

### What happens if results are significant in one study but not in another?

When one study finds a significant result and another does not, it usually means the evidence is mixed rather than one study “proving” and the other “disproving” the effect.

Differences in sample size, study design, measurement precision, and random variation can explain the discrepancy.

Looking at the effect sizes, confidence intervals, and results from multiple studies (meta-analysis) is the best way to judge the overall evidence.

### Further Information

- P Value Calculator From T Score

- P-Value Calculator For Chi-Square

- P-values and significance tests (Kahn Academy)

- Hypothesis testing and p-values (Kahn Academy)

- Wasserstein, R. L., Schirm, A. L., & Lazar, N. A. (2019). Moving to a world beyond “p“< 0.05”.

- Criticism of using the “p“< 0.05”.

- Publication manual of the American Psychological Association

- Statistics for Psychology Book Download

### Sources:

Bland, J. M., & Altman, D. G. (1994). One and two sided tests of significance: Authors’ reply.BMJ: British Medical Journal,309(6958), 874.

Camerer, C. F., Dreber, A., Holzmeister, F., Ho, T.-H., Huber, J., Johannesson, M., Kirchler, M., Nave, G., Nosek, B. A., Pfeiffer, T., Altmejd, A., Buttrick, N., Chan, T., Chen, Y., Forsell, E., Gampa, A., Heikensten, E., Hummer, L., Imai, T., … Wu, H. (2018). Evaluating the replicability of social science experiments in Nature and Science between 2010 and 2015.Nature Human Behaviour,2(9), 637-644.

Cohen, J. (1988).Statistical power analysis for the behavioral sciences(2nd ed.). Lawrence Erlbaum Associates.

Cohen, J. (1992). A power primer.Psychological Bulletin,112(1), 155-159.

Cumming, G. (2014). The new statistics: Why and how.Psychological Science,25(1), 7-29.

Dienes, Z. (2011). Bayesian versus orthodox statistics: Which side are you on?Perspectives on Psychological Science,6(3), 274-290.

Fisher, R. A. (1925).Statistical methods for research workers. Oliver & Boyd.

Gilbert, D. T., King, G., Pettigrew, S., & Wilson, T. D. (2016). Comment on “Estimating the reproducibility of psychological science.”Science,351(6277), 1037.

Goodman, S. N., & Royall, R. (1988). Evidence and scientific research.American Journal of Public Health,78(12), 1568-1574.

Goodman, S. (2008, July).A dirty dozen: twelve p-value misconceptions. InSeminars in hematology(Vol. 45, No. 3, pp. 135-140). WB Saunders.

Lang, J. M., Rothman, K. J., & Cann, C. I. (1998). That confounded P-value.Epidemiology (Cambridge, Mass.),9(1), 7-8.

Open Science Collaboration. (2015). Estimating the reproducibility of psychological science.Science,349(6251), aac4716.

Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant.Psychological Science,22(11), 1359-1366.

Wasserstein, R. L., & Lazar, N. A. (2016). The ASA statement on p-values: Context, process, and purpose.The American Statistician,70(2), 129-133.

McLeod, S. (2026). P-Value Significance. Simply Psychology. https://www.simplypsychology.org/p-value.html

McLeod, Saul. "P-Value Significance." Simply Psychology, 18 September 2026, https://www.simplypsychology.org/p-value.html.

McLeod, S. (2026) P-Value Significance. Simply Psychology. Available at: https://www.simplypsychology.org/p-value.html (Accessed: 22 September 2026).

Olivia Guy-Evans, MSc

BSc (Hons) Psychology, MSc Psychology of Education

Associate Editor for Simply Psychology

Olivia Guy-Evans is a writer and associate editor for Simply Psychology, where she contributes accessible content on psychological topics. She is also an autistic PhD student at the University of Birmingham, researching autistic camouflaging in higher education.

Chartered Psychologist (CPsychol)

BSc (Hons) Psychology, MRes, PhD, University of Manchester

Saul McLeod, PhD, is a qualified psychology teacher with over 18 years of experience in further and higher education. He has been published in peer-reviewed journals, including the Journal of Clinical Psychology.
