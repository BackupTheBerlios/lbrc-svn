/*
 * Created on Nov 15, 2005
 *
 * To change the template for this generated file go to
 * Window&gt;Preferences&gt;Java&gt;Code Generation&gt;Code and Comments
 */
package org.json.lang;

import org.json.io.Serializable;
/*
 * Licensed Materials - Property of IBM,
 * (c) Copyright IBM Corp. 1998, 2002  All Rights Reserved
 */

/**
 * Number is the abstract superclass of the classes
 * which represent numeric base types (i.e. all but
 * Character, Boolean, and Void).
 *
 * @author		OTI
 * @version		initial
 */
public abstract class Number implements Serializable{

	static final long serialVersionUID = -8742448824652078965L;

/**
 * Number constructor.
 * Included for spec compatability.
 */
public Number() {
}

/**
 * Answers the byte value which the receiver represents
 *
 * @author		OTI
 * @version		initial
 *
 * @return		byte		the value of the receiver.
 */
public byte byteValue () {
	return (byte) intValue();
}

/**
 * Answers the double value which the receiver represents
 *
 * @author		OTI
 * @version		initial
 *
 * @return		double		the value of the receiver.
 */
public abstract double doubleValue();

/**
 * Answers the float value which the receiver represents
 *
 * @author		OTI
 * @version		initial
 *
 * @return		float		the value of the receiver.
 */
public abstract float floatValue();

/**
 * Answers the int value which the receiver represents
 *
 * @author		OTI
 * @version		initial
 *
 * @return		int		the value of the receiver.
 */
public abstract int intValue();

/**
 * Answers the long value which the receiver represents
 *
 * @author		OTI
 * @version		initial
 *
 * @return		long		the value of the receiver.
 */
public abstract long longValue();

/**
 * Answers the short value which the receiver represents
 *
 * @author		OTI
 * @version		initial
 *
 * @return		short		the value of the receiver.
 */
public short shortValue() {
	return (short) intValue();
}

}
