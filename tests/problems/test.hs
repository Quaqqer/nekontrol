main = do
  interact (show . (*2) . read)
