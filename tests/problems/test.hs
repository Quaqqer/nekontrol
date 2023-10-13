main = do
  interact ((++"\n") . show . (*2) . read)
