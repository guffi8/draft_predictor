OutputDraftFeatures <- function(filePathInput, filePathOutput){
  #reading the file
  ex = read.table(filePathInput, header = T, sep = "\t");
  attach(ex)
  names(ex)
  
  #turning conference and class to categorical variables
  catConf <- cut(CONF, breaks = c(9), labels = c("ACC", "PAC-12", "SEC","BIG-TEN","BIG-12","BIG-EAST","MWC","AAC","Other"));
  CatYear <- cut(YEAR, breaks = c(5), labels = c("Freshman","Sophmore","Junior","Senior", "Graduate"))
  
  #computing the model
  mod <- lm (Rank ~ ORB + DRB + AST + STL + BLK + TOV + PF + PTS + FTPER + FGPER + THRPER + catConf + CatYear);
  
  summ = summary(mod)
  
  #writing to a file
  x=summ$coefficients[0:24]
  write(x, file = filePathOutput,
        ncolumns = 1,
        append = FALSE, sep = "\n")
}

OutputDraftFeatures("training_data/All.txt", "Vectors/FeatureWeightsAll.txt");
OutputDraftFeatures("training_data/Guards.txt", "Vectors/FeatureWeightsGuards.txt");
OutputDraftFeatures("training_data/Forwards.txt", "Vectors/FeatureWeightsForwards.txt");
OutputDraftFeatures("training_data/Centers.txt", "Vectors/FeatureWeightsCenters.txt")

