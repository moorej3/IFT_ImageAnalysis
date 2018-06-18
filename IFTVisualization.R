Data <- read.csv("Data.csv")
Data$Strain <- substr(Data$Sample, 12,20)
#Data$Strain <- substr(Data$Sample, 12,15)
head(Data)

library(mosaic)
library(ggpubr)

#Distribution of sizes
ggplot(Data, aes(x = flalength, color = Strain)) + geom_density()

#Boxplot of velocity vs strain
ggplot(Data, aes(x = Strain, y = avgSlope)) + 
  geom_boxplot() + 
  ggtitle("Velocity")+
  theme_pubr()+
  ylab("Average Velocity (um/s)")

ggplot(Data, aes(x = flalength, y = avgSlope, color = Strain)) +
  geom_point()+
  geom_smooth(method = "lm", se = F)+
  ylab("IFT Velocity")+
  theme_pubr()

#Injection Intensity
Data$InjInt <- Data$totalInt/ Data$flalength * Data$avgSlope
ggplot(subset(Data), aes(x = flalength, y = InjInt, color = Strain)) + 
  geom_point()+
  geom_smooth(method = "lm", se = F)+
  ylab("Injection Intensity")+
  xlab("Flagella Length")+
  theme_pubr()


