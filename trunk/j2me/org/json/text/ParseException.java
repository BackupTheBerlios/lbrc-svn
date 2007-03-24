/*
 * Created on Nov 15, 2005
 *
 * To change the template for this generated file go to
 * Window&gt;Preferences&gt;Java&gt;Code Generation&gt;Code and Comments
 */
package org.json.text;

/*
 * Licensed Materials - Property of IBM,
 * (c) Copyright IBM Corp. 1998, 2002  All Rights Reserved
 */

/**
 * A ParseException is thrown when the String being parsed
 * is not in the correct form.
 *
 * @author		OTI
 * @version		initial
 */

public class ParseException extends Exception {

	static final long serialVersionUID = 2703218443322787634L;

	private int errorOffset;

/**
 * Constructs a new instance of this class with its
 * walkback, message  and the location of the error
 * filled in.
 *
 * @author		OTI
 * @version		initial
 *
 * @param		detailMessage String
 *				The detail message for the exception.
 * @param		location int
 *				The index at which the parse exception occurred.
 */
public ParseException (String detailMessage, int location) {
	super(detailMessage);
	errorOffset = location;
}

/**
 * Answers the index at which the parse exception occurred.
 *
 * @author		OTI
 * @version		initial
 *
 * @return		int
 *				The index of the parse exception.
 */
public int getErrorOffset () {
	return errorOffset;
}

}
