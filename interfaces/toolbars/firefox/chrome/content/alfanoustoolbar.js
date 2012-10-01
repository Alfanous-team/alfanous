/*
	alfanoustoolbar.js file 
	created on Sunday, August 05th, 2012 at 13:00
	by SMAHI Zakaria
	zakaria08esi@gmail.com
*/

/*
TODO  LIST
	# open  links in  new tab instead of getting last browser window  ......... done
	# use one regexp to trim " "  ......... done
	# enable search history and autocomplete......done
 */


	function AlfanousTB_Search(event, type)
	{

		/*
			AlfanousTB_Search function
			This function performs a search in alfanous
			if the SearchBox is empty it loads the alfanous default URL (HomePage) 
		*/		
		
		var URL = ""; // using this variable to holding on the URL

		var isEmpty = false; // is the SearchBox Empty or not? initially is false we suppose that the user will search for a word

		// Get a handle to our search terms box (the <menulist> element)

		var searchTermsBox = document.getElementById("AlfanousTB-Search-textbox");
    
		// Get the value in the search terms box, trimming whitespace as necessary using the AlfanousTB_TrimString() function
		// See farther down in this file for details on how it works.

		var searchTerms = AlfanousTB_TrimString(searchTermsBox.value);

		if(searchTerms.length == 0) // Is the search terms box empty?
		isEmpty = true;             // If so, set the isEmpty flag to true
		else                        // If not, convert the terms to a URL-safe string
		searchTerms = AlfanousTB_ConvertTermsToURI(searchTerms);

		// Now switch on whatever the incoming type value is
		// If the search box is empty, we simply redirect the user to alfanous homepage
		// if not perform a full search.

		switch(type)
		{

			// Build up the URL
			case "word":
			if(isEmpty) { URL = "http://www.alfanous.org/"; }
			else        { URL = "http://www.alfanous.org/?search=" + searchTerms; }
			break;
		
		}

		// Load the URL in the browser window using the AlfanousTB_LoadURL function
		AlfanousTB_LoadURL(URL);
		AlfanousTB_Add();

	}

	function AlfanousTB_TrimString(string)
	{

		/*
			AlfanousTB_TrimString function
			This function trims all leading and trailing whitespace from the incoming string 
			and convert them into one 
			whitespace; the new string is returned 
		*/

		// If the incoming string is invalid, or nothing was passed in, return empty
		if (!string)
		return "";
		
		string = string.replace(/(^\s*)|(\s*$)/g,""); // Remove leading and trailing whitespace
		string = string.replace(/\s+/g, ' '); // Replace all whitespace runs with a single space
		return string; // Return the altered value

	}

	function AlfanousTB_ConvertTermsToURI(terms)
	{
		
		/*
			AlfanousTB_ConvertTermsToURI
			This function converts an incoming string of search terms
			to a safe value for passing into a URL
		*/

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

	function AlfanousTB_LoadURL(url)
	{
		
		/*
			AlfanousTB_LoadURL
			This function loads the specified URL in the browser (new tab)
		*/
		gBrowser.selectedTab = gBrowser.addTab(url);
	}

	function AlfanousTB_KeyHandler(event)
	{
	
		/*
			AlfanousTB_KeyHandler
			This function checks if the [enter] button was pressed
			if yes; it loads the AlfanousTB_Search function and as parameters the text in SearchBox
		*/
		
		// Was the key that was pressed [ENTER]? If so, perform a web search.
		if(event.keyCode == event.DOM_VK_RETURN)
		AlfanousTB_Search(event, 'word');

	}


	// add autocomplete function here 
	function AlfanousTB_Add()
	{

		/* 
			AlfanousTB_Add
			This function save the historic search terms
		*/

			var fhService = Components.classes["@mozilla.org/satchel/form-history;1"].getService(Components.interfaces.nsIFormHistory2);
			fhService.addEntry("searchHistory", document.getElementById("AlfanousTB-Search-textbox").value);

	}


