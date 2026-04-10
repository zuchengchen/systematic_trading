# Paragraph Boundary Fix Report (Chapters 7-21)

- 入口文件: `main.tex`
- 原始 PDF: `Systematic Trading A unique new method for designing trading and investing systems-Robert.pdf`
- 处理范围说明: 按本项目 21 个正文单元计，第 7 到 21 章对应 `chapter_six` 到 `appendix_d`。
- 共修复段落边界问题: **152** 处
- 处理方式: 仅通过插入或删除空行恢复 PDF 可明确证明的自然段边界；未改写句子。
- 需人工确认: 无单独标记项；其余未动位置未达到可由 PDF 直接证明的修改阈值，或属于表格/列表/图示结构。

## 实际修改文件
- `chapters/chapter_six.tex`
- `chapters/chapter_seven.tex`
- `chapters/chapter_eight.tex`
- `chapters/chapter_nine.tex`
- `chapters/chapter_ten.tex`
- `chapters/chapter_eleven.tex`
- `chapters/chapter_twelve.tex`
- `chapters/chapter_thirteen.tex`
- `chapters/chapter_fourteen.tex`
- `chapters/chapter_fifteen.tex`
- `chapters/epilogue.tex`
- `chapters/appendix_a.tex`
- `chapters/appendix_b.tex`
- `chapters/appendix_c.tex`
- `chapters/appendix_d.tex`

## 逐项明细
### `chapters/chapter_six.tex`
1. `删除空行` · `Data availability` · `Fundamental trading strategies require yet more kinds of data. The costs of acquiring data on certain instruments, like Gilts perhaps, may be uneconomic for ama`
2. `删除空行` · `Standard deviation` · `In principle my framework can deal equally well both with assets whose returns naturally have low \textbf{standard deviations} and those that are very risky. It`

### `chapters/chapter_seven.tex`
3. `删除空行` · `Forecasts proportional to risk adjusted return` · `Simple, you might think. As I was trading Bunds when I spoke to Sergei then I should set up my \textbf{trading rule} so a weak forecast of 50 would mean a purch`
4. `插入空行` · `Forecasts proportional to risk adjusted return` · `You've seen before that the ratio of average return to standard deviation of returns is the \textbf{Sharpe ratio}. So expected Sharpe ratios make good forecasts`
5. `删除空行` · `Forecasts should have a consistent scale` · `In truth it doesn't really matter, as long as you are consistent, but whichever scaling you choose here will affect the rest of your trading system. In particul`
6. `删除空行` · `Trend following with the EWMAC rule` · `Many asset prices seem to show \textbf{momentum}: what goes up, usually carries on going up; and vice versa. This effect can be captured by using \textbf{trend `
7. `插入空行` · `Trend following with the EWMAC rule` · `Firstly, they work. As we saw in chapter one, the trend following ‘early loss taker' rule made mincemeat of its opposition, the ‘early profit taker'. There's a `
8. `删除空行` · `Trend following with the EWMAC rule` · `is reduced, and then reversed once the fast EWMA climbs back above the slow in June`
9. `插入空行` · `Staunch Systems Trader` · `As I said in chapter three, ‘Fitting', I don't recommend using \textbf{back-tested} profitability to select trading rules or variations. Instead you should focu`
10. `插入空行` · `Staunch Systems Trader` · `You should then use two selection criteria. The first is to avoid including any two variations with more than a 95\% correlation to each other, as one of them w`
11. `插入空行` · `Staunch Systems Trader` · `Secondly, you must exclude anything which trades too slowly, or too quickly. As I mentioned in chapter two, very slow rules are unlikely to generate significant`
12. `插入空行` · `Staunch Systems Trader` · `The \textbf{staunch systems trader} example chapter in part four will give an overview of the rule selection process.`
13. `插入空行` · `Summary of trading rules and forecasts` · `Semi-automatic traders should either have developed their own rules, adapted a publically available rule, or be happy for now to use one or both of the rules I `

### `chapters/chapter_eight.tex`
14. `删除空行` · `Choosing the forecast weights` · `Forecast weights might be the same for all instruments, or different. I'll now show you how to use the \textbf{handcrafting} method I described in chapter four `
15. `插入空行` · `CONCEPT: DIVERSIFICATION MULTIPLIER` · `For the simple example with four rule variations from earlier in the chapter I populated a correlation matrix using the information in appendix C, which is show`
16. `删除空行` · `Capped at 20` · `All the reasons cited in the previous chapter for limiting individual forecasts apply equally to combined forecasts, so I strongly encourage you to limit combin`

### `chapters/chapter_nine.tex`
17. `插入空行` · `The importance of risk targeting` · `Making this decision correctly involves understanding two things. Firstly you must understand your system, in particular its likely performance and whether it's`
18. `插入空行` · `The importance of risk targeting` · `Next you must understand yourself, in a complete and honest way. Can you face the possibility of regularly losing 5\%, 10\% or 20\% of your own capital in a day`
19. `插入空行` · `The importance of risk targeting` · `These points also apply to those paid to manage other people's money. Additionally professionals need to understand their clients' tolerance for losing money. I`
20. `插入空行` · `Setting a volatility target` · `In the rest of the chapter I'll be dealing with the implications of where you set your trading capital and percentage volatility target, rather than setting you`
21. `插入空行` · `Setting a volatility target` · `Here are the points to consider when setting your trading capital and percentage volatility targets:`
22. `插入空行` · `How much can you lose?` · `For an institutional investor things are usually straightforward; you are given £100 million and you would use 100\% of it. Sometimes you might not go ‘all in' `
23. `插入空行` · `How much can you lose?` · `If you're investing your own money then your trading capital will depend on your savings and how much you are willing to commit to such a risky endeavour. In an`
24. `插入空行` · `Can you cope with the risk?` · `I hope so because you're likely to see those kinds of losses within the first few weeks of trading! As table 20 shows, a \$20,000 loss would typically be seen e`
25. `插入空行` · `Can you cope with the risk?` · `With negative skew it's vital to have sufficient capital to cope with the very bad days, weeks and months you will occasionally see. This is especially true wit`
26. `插入空行` · `Can you realise that risk?` · `But if you can't get enough, or any, leverage then you might have a problem achieving your target volatility. If you are buying short-term government bonds with`
27. `插入空行` · `Can you realise that risk?` · `Because it's mostly a problem for non-leveraged \textbf{asset allocating investors} I'll go into more detail about this in the relevant part of part four, chapt`
28. `删除空行` · `(top)` · `A simple formula can be used to determine how you should set your volatility target, given the underlying \textbf{Sharpe ratio} (SR) of your trading system. You`
29. `插入空行` · `Is this the right level of risk?` · `The short answer is no. There is a Goldilocks level of risk -- not too little and not too much. Even if you are willing and able to go above this level you shou`
30. `插入空行` · `Is this the right level of risk?` · `Naively if you expect to be profitable then you should bet as much as you're allowed to. However this ignores the compounding of returns over time. Suppose you `
31. `插入空行` · `Is this the right level of risk?` · `Nearly all professional gamblers, many professional money managers and some amateurs in both fields know that this optimal point should be calculated using some`
32. `插入空行` · `Is this the right level of risk?` · `You can see this in figure 21, where for an SR 0.5 system the best performance is achieved with the optimal 50\% volatility target. This is true for all three s`
33. `插入空行` · `Is this the right level of risk?` · `Unfortunately many people with capital of \$20,000 will conclude it's possible to earn 400\% a year, or \$80,000, as full-time traders. There are also plenty of`
34. `插入空行` · `Is this the right level of risk?` · `Even if you had a crystal ball, and knew your expected Sharpe precisely, you could be unlucky and have a decade or more of sub-par performance. Figure 21 shows `
35. `插入空行` · `Recommended percentage volatility targets` · `Column C of table 26 shows the correct targets given asset allocators' SR expectations. However, as you'll see in chapter fourteen, it's unlikely even this leve`
36. `插入空行` · `Recommended percentage volatility targets` · `Semi-automatic traders have systems which cannot be back-tested and usually have a small, relatively un-diversified, set of ad-hoc instruments. I would initiall`
37. `插入空行` · `Recommended percentage volatility targets` · `Again the target should be halved if you are trading a strategy that is likely to have negative skew, such as selling option volatility, or exhibits a similar r`
38. `插入空行` · `When the percentage volatility target should be changed` · `To avoid this scenario it’s better to start with significantly lower \textbf{trading capital} and gradually increase it until you have the full amount invested.`
39. `插入空行` · `What percentage of capital per trade?` · `Table 27 gives the results, assuming an average of two positions are held at once. If a greater or fewer number are traded on average, then you just need to mul`
40. `删除空行` · `What percentage of capital per trade?` · `This all sounds fairly sedate but from the table this works out to a suicidal 160\% volatility target. If this target is \textbf{Kelly optimal} then the achieva`

### `chapters/chapter_ten.tex`
41. `插入空行` · `Position block and block value` · `These definitions will seem trivial to equity investors. ‘One' Apple share is exactly that -- one Apple share. If a share has a price of \$400 it will cost exac`
42. `插入空行` · `Position block and block value` · `But life isn't always that simple. For example you can use a UK financial spread betting firm to bet on the FTSE falling at £10 a point. If the FTSE rises 1\% f`
43. `插入空行` · `Position block and block value` · `Futures contracts also have non-trivial block values. WTI crude oil futures on NYMEX are quoted in dollars per barrel. But each futures contract is for 1000 bar`
44. `插入空行` · `Position block and block value` · `A Eurodollar future represents the cost of nominally borrowing \$1 million for three months and is priced at 100 minus the annual interest rate. If the price ri`
45. `插入空行` · `CONCEPT: MEASURING RECENT STANDARD DEVIATION` · `The first method is to eyeball the chart. If you look at figure 22 you can see that the average daily change in crude oil futures over the last month of the cha`
46. `插入空行` · `Instrument currency volatility` · `In general instrument currency volatility is equal to the block value multiplied by the price volatility. It will be in the same currency in which the block val`
47. `插入空行` · `What's that in real money?` · `The instrument currency volatility needs to be converted to an instrument value volatility using an appropriate exchange rate. The exchange rate will have the c`
48. `插入空行` · `What's that in real money?` · `As an example for a UK investor with a GBP account, the instrument currency volatility of a crude oil future (\$997.50) will need to be multiplied by the curren`
49. `插入空行` · `Volatility target and position risk` · `We also assume that we get the required target risk by having a constant amount of expected volatility from owning a fixed long position in the asset. So we won`
50. `插入空行` · `Volatility target and position risk` · `For the investor in the example to get the entire required daily standard deviation of £62,500 from being long crude oil futures they need to buy £62,500, divid`
51. `插入空行` · `Volatility target and position risk` · `In general the volatility scalar is equal to your daily cash volatility target, divided by the instrument value volatility. You'll notice that both of these var`

### `chapters/chapter_eleven.tex`
52. `删除空行` · `(top)` · `In practice though you're going to share your capital across a portfolio of subsystems; similar to the way I created a portfolio with the same three underlying `
53. `插入空行` · `This section is suitable for all readers` · `As I'll show you later in the chapter you also need to account for the effect of portfolio diversification. But first we need to consider how to calculate the i`
54. `删除空行` · `Instrument diversification multiplier` · `Once you've parcelled out your \textbf{trading capital} to each \textbf{trading} \textbf{subsystem} you're faced with a problem you might have seen before in ch`
55. `插入空行` · `Instrument diversification multiplier` · `You already know that the correlation between the two equity indices and the bond in the simple example is very low (the rule of thumb value from table 50 in ap`
56. `插入空行` · `Semi-automatic Trader` · `I advocate that the multiplier is limited to a maximum of 2.5, since if you end up frequently trading more than your average then your expected risk will be too`
57. `插入空行` · `This section is relevant to all readers` · `I'm assuming that I use futures to trade these assets and that I have an \textbf{annualised cash} \textbf{volatility target} of €100,000. The price volatility a`
58. `插入空行` · `This section is relevant to all readers` · `Finally I can calculate the size of any trade needed. I recommend that if the current position is within 10\% of the rounded target position, then you shouldn't`
59. `插入空行` · `This section is relevant to all readers` · `So for example if I had a target position of 50 crude oil contracts and my current position was between 45 and 55 contracts then I wouldn't bother trading. Conv`
60. `删除空行` · `This section is relevant to all readers` · `Trades can be done manually or by an algorithm if you have a completely automated system. There is information on how I automate my own trading with simple algo`

### `chapters/chapter_twelve.tex`
61. `插入空行` · `Speed and Size` · `In this chapter I will look at how you should design your \textbf{trading systems} given these two interrelated issues of speed and account size.`
62. `插入空行` · `Speed of trading` · `Overtrading is a result of overconfidence, one of the \textbf{cognitive biases} I discussed in chapter one. Only someone who was very bullish would assume the r`
63. `插入空行` · `Speed of trading` · `In the next part of the chapter I'm going to show you how to calculate the cost of trading a particular instrument at a given speed, and how to work out the lik`
64. `插入空行` · `The cost of execution` · `Smaller traders can assume they will pay at most half the usual spread between bid and offer in execution cost, which is what you get from submitting a market o`
65. `插入空行` · `The cost of execution` · `This assumption is reasonable if your typical trade is less than the usual size available on the inside of the spread. Larger traders cannot assume this, and I `
66. `插入空行` · `Standardising cost measurement` · `The third type of instrument we'll consider is \textbf{exchange traded funds (ETFs)}. Like many equities, these are cheaper to trade in 100 share blocks. The pr`
67. `插入空行` · `Setting a speed limit` · `What if you had an alternative rule, with a turnover of 100, but with a pre-cost return of 0.60 SR? Though your costs have doubled to 0.20 SR, the net return ha`
68. `插入空行` · `Setting a speed limit` · `In chapter three when I discussed \textbf{fitting} I pointed out that there is always considerable uncertainty about expected pre-cost performance. An implicati`
69. `插入空行` · `Setting a speed limit` · `It also means you need a lot of data to make it probable that one trading rule had better performance in the past than another. So considerable evidence is requ`
70. `插入空行` · `Setting a speed limit` · `The relative pre-cost Sharpe ratio you will achieve in practice is extremely uncertain, whilst expected costs can be predicted with much more accuracy. There is`
71. `插入空行` · `Setting a speed limit` · `A fast trading rule might look great in the past, but if the market was very expensive nobody could have actually exploited it. Now costs have fallen there is a`
72. `插入空行` · `Setting a speed limit` · `To ensure you don't chase performance, or trade faster than was viable in the past, I recommend that you set a \textbf{speed limit}; a maximum expected turnover`
73. `插入空行` · `Setting a speed limit` · `At the start of this chapter I said I wouldn't trade a strategy which paid two-thirds of its profits out as costs, amounting to 1.0 in SR annually. I personally`
74. `插入空行` · `Which instruments to trade?` · `If you use my recommended maximum of 0.08 \textbf{Sharpe ratio (SR)} units paid annually in costs for \textbf{asset allocating investors} and \textbf{semi-autom`
75. `插入空行` · `Which instruments to trade?` · `The table also shows the lower limit on how slowly you can trade a particular kind of system, with a minimum achievable turnover in round trips per year. Given `
76. `插入空行` · `Staunch systems trader` · `Using my recommended guideline for setting \textbf{speed limits} from above you don't want costs greater than 0.13 \textbf{Sharpe ratio (SR)}. So you should be `
77. `插入空行` · `Staunch systems trader` · `It is simplest to use the same trading rules and variations for all the \textbf{instruments} you trade. This means you will need to drop any rules which are too`
78. `插入空行` · `Staunch systems trader` · `However if the set of instruments you have features trading costs that vary significantly you might consider using faster variations only with the cheapest inst`
79. `插入空行` · `This section is relevant to all readers` · `Alternatively if you're using the suggested figures for Sharpe ratio in the relevant chapters of part four, then there's nothing more to do as all these assumpt`
80. `插入空行` · `Trading with a lot of capital` · `They have three options when they submit the order. Firstly they can cross the spread and submit a single market order. They will get 3,369 for the first 437 lo`
81. `插入空行` · `Trading with a lot of capital` · `Secondly they can offer 5,000 lots at 3,370, adding to the 7 lots already on the order book. They might get lucky and meet a large buyer who takes their offer. `
82. `插入空行` · `Trading with a lot of capital` · `Finally the funds human traders or execution algorithims can break the order up into chunks and execute it gradually. The order will take longer to execute and `
83. `插入空行` · `Trading with a lot of capital` · `In none of these three cases is the execution cost guaranteed to be exactly 0.5 points. If you are trading in large size, in relatively illiquid markets and rel`
84. `插入空行` · `Asset Allocating Investor / Staunch Systems Trader` · `The principle you should follow is to hold the most diversified portfolio possible without running into any problems with maximum positions. Ideally you want at`
85. `插入空行` · `Asset Allocating Investor / Staunch Systems Trader` · `You then only add additional instruments to an asset class if this doesn't cause a small maximum position problem to appear either in the new instrument or in a`
86. `插入空行` · `Semi-automatic Trader` · `Remember from chapter eleven, ‘Portfolios', (page 169) that your portfolio weights are 100\% divided equally by the maximum number of bets you're likely to make`

### `chapters/chapter_thirteen.tex`
87. `插入空行` · `Who are you?` · `It will not be easy sticking to the framework. The system may force you to trade, or prevent you from trading, when you would rather do otherwise. However there`
88. `插入空行` · `Who are you?` · `In the specific example discussed in this chapter we'll assume you're going to be trading spread bets on equity indices and FX, as reasonable sized amateur inve`
89. `插入空行` · `Who are you?` · `As a semi-automatic trader you'll be trading sporadically as opportunities arise. This presents some challenges in using my systematic framework, which normally`
90. `插入空行` · `Who are you?` · `To reduce the workload you'll first do some daily housekeeping on your current portfolio: closing out any positions that have hit stop losses, adjusting estimat`
91. `插入空行` · `Who are you?` · `If you're trading part-time you will leave stop loss orders with your broker and go to your day job. However if you're trading full-time you'll continue to watc`
92. `插入空行` · `Instrument choice: size and costs` · `You'll be using quarterly spread bets, with all bets in multiples of £1 per point. For example if you go long the FTSE at £2 per point, and it goes from 6500 to`
93. `插入空行` · `Instrument choice: size and costs` · `You should also check that the \textbf{standardised costs} of trading any potential instrument will be 0.01 \textbf{Sharpe ratio} units or less, for reasons exp`
94. `插入空行` · `Forecasts and stop losses` · `The stop loss rule is loosely related to the ‘early loss taker’ system I’ve used for examples in previous chapters. It uses stops set at a multiple of the curre`
95. `插入空行` · `Forecasts and stop losses` · `Also in chapter twelve (page 183) I suggested you use a costs figure of 0.01 SR units as the standardised cost for all of your spread bets. The table shows you `
96. `插入空行` · `Forecasts and stop losses` · `I don't advise using different stop loss systems for different instruments as this complicates life and can lead to mistakes. So the value of X should be set co`
97. `插入空行` · `Forecasts and stop losses` · `In this chapter we are going to use an X of 4, which means I assume you're predicting trends that last for just over six weeks.`
98. `插入空行` · `Forecasts and stop losses` · `Note that unlike in the original ‘early loss taker' system you won't be using a profit target. Why not? My own research shows no evidence that systematic profit`
99. `插入空行` · `Forecasts and stop losses` · `To summarise you mustn't close your trade until you hit a stop loss; then you must close it. Sticking to this rule will be difficult, but will mean that your ri`
100. `删除空行` · `(top)` · `This implies you'll have an annual \textbf{volatility target} of £100,000 × 15\% = £15,000 and a daily target of £15,000 ÷ 16 = £937.50.\footnote{As before to g`
101. `插入空行` · `Volatility targeting` · `You'll be measuring your account value daily, recalculating \textbf{trading capital}, and adjusting your \textbf{volatility target} accordingly. This might trig`
102. `删除空行` · `Position sizing` · `You can now think about ‘Position sizing', as discussed in chapter ten. First you need to measure the recent percentage \textbf{standard deviation} of returns (`
103. `插入空行` · `Position sizing` · `I'd suggest you use the eyeball technique described in chapter ten (page 155), which you're already using to calculate the volatility estimate needed for stop l`
104. `插入空行` · `Position sizing` · `From table 38 (page 212) with the suggested X of 4 you would expect to get a turnover of 8 after accounting for the effects of sizing your position. With \textb`
105. `插入空行` · `Position sizing` · `With 15\% annualised volatility that equates to a performance drag from costs of 0.08 × 15\% = 1.2\% a year. This is more than most \textbf{passive ETFs}, but s`
106. `插入空行` · `Position sizing` · `You can save on costs by following the advice in the chapter twelve, ‘Speed and Size', and not adjusting your estimate of \textbf{instrument currency volatility`
107. `插入空行` · `Position sizing` · `As you're spread betting, the value of a 1\% move (the \textbf{block value}) depends on the bet size in pounds per point, so you won't need to use exchange rate`
108. `插入空行` · `Portfolios` · `The \textbf{instrument diversification multiplier} will be the maximum number of bets divided by the average. This multiplier ensures the total average absolute`
109. `插入空行` · `Portfolios` · `If you already have your maximum number of bets on, and you desperately need to make a new bet, then sorry: you can't. Wait until one of your existing bets has `
110. `插入空行` · `Portfolios` · `Earlier I said you shouldn't change the forecast on an existing bet. However you can add to positions by placing a new, separate, bet on an instrument which you`
111. `插入空行` · `Portfolios` · `This can't be used as a loophole to close positions; you can't put on a new bet which will make your existing position smaller or reverse it. Finally, to avoid `
112. `插入空行` · `Portfolios` · `In this chapter I am going to assume you have a maximum of four positions, with an average of three. So each position will have an instrument weight of 100\% ÷ `
113. `插入空行` · `Portfolios` · `As you saw in chapter nine, ‘Volatility targeting', (page 150) the use of systematic stop losses allows you to compare my framework with traditional money manag`
114. `插入空行` · `Portfolios` · `X × forecast × percentage volatility target) ÷ (10 × 16 × average number of bets)`
115. `插入空行` · `Portfolios` · `In this example with an X of 4, the average forecast of 10, a 15\% volatility target and an average of three positions you are putting (4 × 10 × 15\%) ÷ (10 × 1`
116. `插入空行` · `Trading in practice` · `Stop losses on existing positions will also need to be adjusted if price volatility changes. They also need to be moved up if prices reach new highs (for longs)`
117. `插入空行` · `Trading in practice` · `Part-time daily traders should then update the stop loss limits they have left with their brokers and go to work at their real jobs. If you're still trading int`
118. `插入空行` · `29 October 2014` · `I feel very strongly about the S\&P bet now and I'm going to add to my position. So I will bet a separate +25 forecast, taking me up to the maximum of +40 for a`

### `chapters/chapter_fourteen.tex`
119. `插入空行` · `Who are you?` · `To get access to different \textbf{asset classes} I assume you'll be using \textbf{exchange traded funds} (ETFs), which are relatively cheap \textbf{collective `
120. `插入空行` · `Who are you?` · `Your imaginary pension fund trustees have specified some constraints on the portfolio. You can only invest in bonds and equities, and no more than 40\% of your `
121. `插入空行` · `Who are you?` · `An extension to the basic example will be to adjust \textbf{instrument weights} according to some expectations about asset \textbf{Sharpe ratios}. These aren't `
122. `删除空行` · `(top)` · `The costs of ETFs will vary depending on their volatility, so we'll conservatively use the standardised cost for the lowest risk ETF (IGIL: global inflation lin`
123. `插入空行` · `Instrument choice: diversification, costs, volatility and size` · `There are several other considerations when choosing ETFs and you should consult one of the books mentioned in appendix A to understand these. Finally, this sel`
124. `插入空行` · `Instrument choice: diversification, costs, volatility and size` · `Table 39 shows the final set of instruments. In the example you're constrained in your portfolio allocations by an outside investor. You have limits on how much`
125. `插入空行` · `The no-rule trading rule, position sizing and costs` · `Because ETFs are quite expensive you should follow the advice in chapter twelve, ‘Speed and Size' (page 196), and use a relatively slow 20 week (100 business da`
126. `插入空行` · `The no-rule trading rule, position sizing and costs` · `With a 20 week look-back the \textbf{turnover} of your trades, in round trips per year, will be 0.4 times a year. If you use the \textbf{speed limit} I recommen`
127. `插入空行` · `Volatility target calculation` · `Working out the achievable \textbf{volatility target} given limited \textbf{leverage} is a two step process. The first step involves making an initial guess as `
128. `删除空行` · `(top)` · `You should use column B ‘Without certainty' in the table, which reflects the difficulty in guessing how assets will perform. As an example, if the average SR ac`
129. `插入空行` · `Portfolios: Using predictions of performance` · `You could do this within the framework by using discretionary forecasts, which would make this example look more like the \textbf{semi-automatic trader} of the `
130. `插入空行` · `Portfolios: Using predictions of performance` · `Don't forget to renormalise the weights to add up to 100\% after adjustment. Please note that you don't need to change your \textbf{instrument diversification m`
131. `插入空行` · `Weekly process` · `Detailed calculations are shown in the trading diary section which follows.`
132. `删除空行` · `10 October 2008` · `The equity markets fell off a cliff last week so you've come in on Saturday to assess the damage. Fortunately your portfolio is diversified enough that your los`
133. `插入空行` · `10 October 2008` · `But there has been some pain -- your current capital is now down to €9,126,500.`

### `chapters/chapter_fifteen.tex`
134. `插入空行` · `Instrument choice: Size, diversification and costs` · `In my opinion the set shown in table 42 is a good selection for this account size.\footnote{These instruments also have the advantage that long histories of dai`
135. `插入空行` · `Instrument choice: Size, diversification and costs` · `In chapter six, ‘Instruments', I said you should also consider skew and volatility when choosing instruments. With a short position the European equity volatili`
136. `插入空行` · `Selecting trading rules` · `For simplicity in this example chapter let's drop the fast variations and use the three slowest (EWMAC 16, 32 and 64), all of which are acceptable even with the`
137. `插入空行` · `Position sizing and measuring price volatility` · `Currencies for each instrument are shown in table 42 and you'll update FX rates daily. You will be using a moving average of recent daily returns to find the \t`
138. `删除空行` · `(top)` · `To avoid distorting the instrument weights too much, I propose putting 30\% of the portfolio into the equities top level group, rather than the 25\% that handcr`
139. `插入空行` · `Portfolio of trading subsystems` · `Additionally you are constrained by the minimum contract size problems which I discussed in chapter twelve, ‘Speed and Size'. In particular the Euro Stoxx futur`
140. `插入空行` · `Portfolio of trading subsystems` · `I'm comfortable with this adjustment, since the alternative is not to trade equities at all, but a larger shift in weights would concern me.`

### `chapters/epilogue.tex`
141. `删除空行` · `Epilogue` · `Thriftiness is another virtue. Know your trading costs. Stick to \textbf{speed limits}: I recommend you set your \textbf{turnover} so you never spend more than `
142. `插入空行` · `Epilogue` · `So it only remains for me to say: Good Luck!`

### `chapters/appendix_a.tex`
143. `插入空行` · `Sources of free data` · `Many brokers and exchanges provide access to live prices, usually with a 15 minute delay. This delay is not problematic unless you are trading on a high frequen`

### `chapters/appendix_b.tex`
144. `插入空行` · `Specification` · `Here are some interesting characteristics of the A and B system.`
145. `删除空行` · `The exponentially weighted moving average crossover (EWMAC) rule` · `In this version of the rule I assume you are working with daily prices for the relevant instrument, with no weekends in the price series. It is possible to work`
146. `插入空行` · `Which pairs of look-backs to use?` · `Beyond the pair 64:256 \textbf{turnover} the holding period gets excessively long, and as the \textbf{law of active management} suggests performance will be poo`

### `chapters/appendix_c.tex`
147. `插入空行` · `How should you select return periods?` · `In this case you need to do ‘block' bootstrapping. Each subset will consist of an appropriate number of consecutive returns. The only randomness is in the choic`
148. `插入空行` · `How long should each period be?` · `This subject has been examined in some depth by academic researchers. My own analysis suggests that there is a small benefit from using longer periods; perhaps `
149. `插入空行` · `How long should each period be?` · `A good rule of thumb is to use samples of returns equal in length to 10\% of the period of history available. So if you had 30 years of data then you should use`
150. `插入空行` · `Rule of thumb correlations` · `For \textbf{staunch systems traders} with \textbf{dynamic} forecasts a good rule of thumb is that the correlation between instrument subsystem returns will be a`

### `chapters/appendix_d.tex`
151. `删除空行` · `Calculating price volatility from historic data` · `EWMA given a smoothing parameter A is:`
152. `插入空行` · `Calculating price volatility from historic data` · `Assuming you've put 0.054 into cell AA1, and the returns are in column B, in column C we get the squared returns:`

