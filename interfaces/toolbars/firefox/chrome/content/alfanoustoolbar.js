////////////////////////////////////////////////////////////////////////////////
// The TutTB_Search() function will perform a Google search for us. The two
// parameters that get passed in are the event that triggered this function
// call, and the type of search to perform.
////////////////////////////////////////////////////////////////////////////////
function TutTB_Search(event, type)
{
    // This variable will hold the URL we will browse to
    var URL = "";

    // This variable will tell us whether our search box is empty or not
    var isEmpty = false;

    // Get a handle to our search terms box (the <menulist> element)
    var searchTermsBox = document.getElementById("TutTB-SearchTerms");
    
    // Get the value in the search terms box, trimming whitespace as necessary
    // See the TutTB_TrimString() function farther down in this file for details
    // on how it works.
    var searchTerms = TutTB_TrimString(searchTermsBox.value);

    if(searchTerms.length == 0) // Is the search terms box empty?
        isEmpty = true;         // If so, set the isEmpty flag to true
    else                        // If not, convert the terms to a URL-safe string
        searchTerms = TutTB_ConvertTermsToURI(searchTerms);

    // Now switch on whatever the incoming type value is
    // If the search box is empty, we simply redirect the user to the appropriate
    // place at the Google website. Otherwise, we search for whatever they entered.

    switch(type)
    {
    // Build up the URL for an image search
    case "aya":
        if(isEmpty) { URL = "http://alfanous.sourceforge.com/"; }
        else        { URL = "http://alfanous.sourceforge.com/index.php?query=" + searchTerms; }
        break;


    }
    
    // Load the URL in the browser window using the TutTB_LoadURL function
    TutTB_LoadURL(URL);
}

////////////////////////////////////////////////////////////////////////////////
// The TutTB_TrimString() function will trim all leading and trailing whitespace
// from the incoming string, and convert all runs of more than one whitespace
// character into a single space. The altered string gets returned.
////////////////////////////////////////////////////////////////////////////////
function TutTB_TrimString(string)
{
    // If the incoming string is invalid, or nothing was passed in, return empty
    if (!string)
        return "";

    string = string.replace(/^\s+/, ''); // Remove leading whitespace
    string = string.replace(/\s+$/, ''); // Remove trailing whitespace

    // Replace all whitespace runs with a single space
    string = string.replace(/\s+/g, ' ');

    return string; // Return the altered value
}

////////////////////////////////////////////////////////////////////////////////
// The TutTB_ConvertTermsToURI() function converts an incoming string of search
// terms to a safe value for passing into a URL.
////////////////////////////////////////////////////////////////////////////////
function TutTB_ConvertTermsToURI(terms)
{
    // Create an array to hold each search term
    var termArray = new Array();

    // Split up the search term string based on the space character
    termArray = terms.split(" ");

    // Create a variable to hold our resulting URI-safe value
    var result = "";

    // Loop through the search terms
    for(var i=0; i<termArray.length; i++)
    {
        // All search terms (after the first one) are to be separated with a '+'
        if(i > 0)
            result += "+";

        // Encode each search term, using the built-in Firefox function
        // encodeURIComponent().
        result += encodeURIComponent(termArray[i]);
    }

    return result; // Return the result
}

////////////////////////////////////////////////////////////////////////////////
// The TutTB_LoadURL() function loads the specified URL in the browser.
////////////////////////////////////////////////////////////////////////////////
function TutTB_LoadURL(url)
{
    // Set the browser window's location to the incoming URL
    window._content.document.location = url;

    // Make sure that we get the focus
    window.content.focus();
}

////////////////////////////////////////////////////////////////////////////////
// The TutTB_KeyHandler() function checks to see if the key that was pressed
// is the [Enter] key. If it is, a web search is performed.
////////////////////////////////////////////////////////////////////////////////
function TutTB_KeyHandler(event)
{
    // Was the key that was pressed [ENTER]? If so, perform a web search.
    if(event.keyCode == event.DOM_VK_RETURN)
        TutTB_Search(event, 'aya');
}

////////////////////////////////////////////////////////////////////////////////
// The TutTB_Populate() function places dynamically generated menu items inside
// our toolbar's search box drop-down menu. Although this sample isn't very
// practical, it is provided as an example of how dynamic menu population works.
////////////////////////////////////////////////////////////////////////////////
function TutTB_Populate()
{
    // Get the menupopup element that we will be working with
    var menu = document.getElementById("TutTB-SearchTermsMenu");

    // Remove all of the items currently in the popup menu
    for(var i=menu.childNodes.length - 1; i >= 0; i--)
    {
        menu.removeChild(menu.childNodes.item(i));
    }

    // Specify how many items we should add to the menu
    var numItemsToAdd = 10;

    tempItem.setAttribute("label", "الحمد لله رب العالمين");
    for(var i=0; i<numItemsToAdd; i++)
    {
        // Create a new menu item to be added
        var tempItem = document.createElement("menuitem");

        // Set the new menu item's label
        //tempItem.setAttribute("label", "Dynamic Item Number " + (i+1));

        // Add the item to our menu
        menu.appendChild(tempItem);
    }
}
