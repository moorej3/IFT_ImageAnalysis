Data <- read.csv("Data.csv")
Data$Strain <- substr(Data$Sample, 1,4)
head(Data)

library(mosaic)
library(ggpubr)

#Boxplot of velocity vs strain
ggplot(Data, aes(x = Strain, y = avgSlope)) + 
  geom_boxplot() + 
  ggtitle("Velocity")+
  theme_pubr()+
  ylab("Average Velocity (um/s)")

#Boxplot of intensity vs strain
ggplot(Data, aes(x = Strain, y = avgInt)) + 
  geom_boxplot() + 
  ggtitle("Intensity")+
  theme_pubr()+
  ylab("Average Intensity (A.U.)")


#Statistics
Slope.lm <- lm(avgSlope~Strain, data = Data)
TukeyHSD(Slope.lm)
anova(Slope.lm)

Int.lm <- lm(avgInt~Strain, data = Data)
TukeyHSD(Int.lm)
anova(Int.lm)

favstats(avgInt~Strain, data = Data)
