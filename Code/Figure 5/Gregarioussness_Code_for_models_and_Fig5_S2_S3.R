#library(glmm)
library(ggplot2)
library(effects)
library(lme4)
library(DHARMa)
library(dplyr)

data = read.csv('Lesion_Social_Data_by_sighting_v2.csv', header = T)

## make occurrence of fringe a factor (N and Y) for model determinations
data<- data %>%
  mutate(FringeOccur = case_when(Model.Fringe ==0  ~ "N",
                           Model.Fringe > 0 ~ "Y"
  ))
data$FringeOccur<- as.factor(data$FringeOccur)

## and for manual determinations
data<- data %>%
  mutate(FringeOccurManual = case_when(Manual.Fringe ==0  ~ "N",
                                 Manual.Fringe > 0 ~ "Y"
  ))
data$FringeOccurManual<- as.factor(data$FringeOccurManual)

## For each data point, find whether the model agrees or disagrees
data$results_fringe = as.factor(ifelse(data$FringeOccur == data$FringeOccurManual, 'Agree','Disagree'))

## first test to see the effect of gregariousness on occurrence for model predictions
occ_Model_sight<- glmer(FringeOccur ~Group_size+(1|Year)+(1|ID),data = data, family = binomial)
#check residuals
simulationOutput_min <- simulateResiduals(fittedModel = occ_Model_sight)
testDispersion(simulationOutput_min) #test fit and dispersion
#get summary for significance 
summary(occ_Model_sight)
#export effects as a data frame
eff_df_fringe <- data.frame(effect("Group_size",occ_Model_sight))

######## now repoeat above with manual determinations ########################
occ_Man_sight<- glmer(FringeOccurManual ~Group_size+(1|Year)+(1|ID),data = data, family = binomial)
simulationOutput_min <- simulateResiduals(fittedModel = occ_Man_sight)
testDispersion(simulationOutput_min) #test fit and dispersion
eff_df_fringe2 <- data.frame(effect("Group_size",occ_Man_sight))
summary(occ_Man_sight)

####### Now repeat entire process for spot lesions ##################
## make occurrence of spot a factor (N and Y)
data<- data %>%
  mutate(SpotOccur = case_when(Model.Spot ==0  ~ "N",
                               Model.Spot > 0 ~ "Y"
  ))
data$SpotOccur<- as.factor(data$SpotOccur)

data<- data %>%
  mutate(SpotOccurManual = case_when(Manual.Spot ==0  ~ "N",
                                     Manual.Spot > 0 ~ "Y"
  ))
data$SpotOccurManual<- as.factor(data$SpotOccurManual)

## For each data point, find whether the model agrees or disagrees
data$results_spot = as.factor(ifelse(data$SpotOccur == data$SpotOccurManual, 'Agree','Disagree'))

## run models with model and manual determinations for spot
occ_Model_sight_spot<- glmer(SpotOccur ~Group_size+(1|Year)+(1|ID),data = data, family = binomial)
simulationOutput_min <- simulateResiduals(fittedModel = occ_Model_sight_spot)
testDispersion(simulationOutput_min) #test fit and dispersion
eff_df_spot <- data.frame(effect("Group_size",occ_Model_sight_spot))
summary(occ_Model_sight_spot) #look at effect sizes and signifance

occ_Man_sight_spot<- glmer(SpotOccurManual ~Group_size+(1|Year)+(1|ID),data = data, family = binomial)
simulationOutput_min <- simulateResiduals(fittedModel = occ_Man_sight_spot)
testDispersion(simulationOutput_min) #test fit and dispersion
summary(occ_Man_sight_spot)
eff_df_spot2 <- data.frame(effect("Group_size",occ_Man_sight_spot))


# Create Figure 4 ###
ggplot(data=eff_df_fringe, aes(x = Group_size)) +
  geom_ribbon(aes(ymin = lower, ymax = upper), fill = "rosybrown2", alpha = 0.3) +
  theme(text = element_text(size=15))+
  geom_line(aes(y = fit, color = "Fringe"), size =1.5) + xlab("Gregariousness") +
  ggtitle("Model Predictions")+ theme(plot.title = element_text(hjust = 0.5, size = 20))+
  geom_jitter(data = data, 
             mapping = aes(x = Group_size, y = Model.Fringe),color = "#EF1910",height = 0.03, alpha = 0.35, stroke = NA, size =2)+
  geom_jitter(data = data, 
              mapping = aes(x = Group_size, y = Model.Spot),color = "#1AA4B8", height = 0.03, alpha = 0.35, stroke = NA, size =2)+
  geom_line(data =eff_df_spot, mapping = aes(y = fit, color = "Spot"), size =1.5)+
  geom_ribbon(data = eff_df_spot, mapping = aes(ymin = lower, ymax = upper), fill = "lightsteelblue2", alpha = 0.3) +
  labs(color = "Lesion Type") + 
  scale_color_manual(values = c("Spot" = "#1AA4B8", "Fringe" = "#EF1910"))+
  
  ylab("Probability of Lesion Presence") + ylim(c(0,1))+
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
          panel.background = element_blank(), axis.line = element_line(colour = "black"))

ggplot(data=eff_df_fringe2, aes(x = Group_size)) +
  geom_ribbon(aes(ymin = lower, ymax = upper), fill = "rosybrown2", alpha = 0.3) +
  theme(text = element_text(size=15))+
  geom_line(aes(y = fit, color = "Fringe"), size =1.5) + xlab("Gregariousness") +
  ggtitle("Manual Predictions")+ theme(plot.title = element_text(hjust = 0.5, size = 20))+
  geom_jitter(data = data, 
              mapping = aes(x = Group_size, y = Model.Fringe),color = "#A30000",height = 0.03, alpha = 0.35, stroke = NA, size =2)+
  geom_jitter(data = data, 
              mapping = aes(x = Group_size, y = Model.Spot),color = "#1A84B8", height = 0.03, alpha = 0.35, stroke = NA, size =2)+
  geom_line(data =eff_df_spot2, mapping = aes(y = fit, color = "Spot"), size =1.5)+
  geom_ribbon(data = eff_df_spot2, mapping = aes(ymin = lower, ymax = upper), fill = "lightsteelblue2", alpha = 0.3) +
  labs(color = "Lesion Type") + 
  scale_color_manual(values = c("Spot" = "#1A84B8", "Fringe" = "#A30000"))+
  
  ylab("Probability of Lesion Presence") + ylim(c(0,1))+
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black"))

###### Manual and model do not align, check proportion of agree/disagree at all group sizes
### Supplemental Figure 2

data$results_fringe<-factor(data$results_fringe, levels = c("Disagree", "Agree"))
ggplot(data, aes(Group_size, fill = results_fringe)) + 
  geom_histogram(position="fill", binwidth=20) +scale_fill_manual(values = c("white","grey"), guide = 'none')+
  ylab("Fringe Accuracy") + xlab("Gregariousness")+
  theme(text = element_text(size=15))+
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black"))

data$results_spot<-factor(data$results_spot, levels = c("Disagree", "Agree"))
ggplot(data, aes(Group_size, fill = results_spot)) + 
  geom_histogram(position="fill", binwidth=20) +scale_fill_manual(values = c("white","grey"), guide = 'none')+
  ylab("Spot Accuracy") + xlab("Gregariousness")+
  theme(text = element_text(size=15))+
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black"))

## Data suggests that the disagreement is occuring at larger group sizes
## Let's test to see if this is becuase data quality is worse at larger group sizes

#### Run model to test how the # of photos per dolphin changes as group size increases #####
Photo_model <- glmer.nb(Num.Photo ~ Group_size + (1|Year) + (1|ID), data = data)

# Supplemental Figure 3
plot(allEffects(Photo_model), xlab='Gregariousness', ylab = "Number of photos per individual", main = "") #check effects
summary(Photo_model)

