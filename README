An updated (and much faster) version of pytyle that uses xpybutil and is
compatible with Openbox Multihead.

Due to using xpybutil much of the lower level XCB/xpyb stuff has been factored 
out of pytyle3. Also, because it relies on Openbox Multihead when there is more 
than one monitor active, a lot less state needs to be saved.

As a result, pytyle3 is ~1000 lines while pytyle2 is ~7000 lines. Additionally, 
because of a simpler design, pytyle3's memory footprint is much smaller and is 
actually quite snappier in moving windows on the screen.

