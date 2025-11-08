# Rescaler

![rescaler-thumb](https://github.com/user-attachments/assets/d209c097-3a25-46f9-9ec5-113c912ba773)

**Author:** The French Monkey (TFMSTYLE)  
**Version:** 1.0.0  

---

## Overview

**Rescaler** is a precision tool for **uniformly rescaling multiple objects** to match the bounding box size of a chosen **target object**.  
It allows artists to quickly normalize object dimensions while maintaining proportional scaling and optionally centers them to the target’s position.

This add-on is ideal for **scene alignment**, **kitbashing**, **asset standardization**, and **object comparison** workflows.

---

## Parameters

### Rescaler Target
Defines which object will serve as the reference for scaling.

- **Rescaler Target (string):**  
  The name of the active object designated as the scale reference.  
  *(Automatically updated when a single object is selected.)*

---

### Center Objects to Target After Scaling
- **Type:** Boolean  
- **Description:**  
  When enabled, after scaling, each object’s **bounding box center** is repositioned to align with the target’s bounding box center.  
  *(Default: False)*

---

## Operators

### Set Target from Active
**Operator:** `object.rescaler_set_target`  
Sets the current **active object** as the scaling target.  
Updates `Scene.rescaler_target` automatically.

---

### Clear Target
**Operator:** `object.rescaler_clear_target`  
Clears the current scaling target from the scene, disabling rescaling until a new one is set.

---

### Reset Scale
**Operator:** `object.rescaler_reset_scale`  
Resets the scale of all selected objects to `(1, 1, 1)`.  
Useful for normalizing transformations before applying new scaling.

---

### Rescale to Target
**Operator:** `object.rescaler_apply`  
Rescales all **selected objects (excluding the target)** so that their **largest bounding box dimension** matches the target’s largest dimension.

**Steps performed:**
1. Computes the **world-space bounding box** for the target and selected objects.  
2. Determines the **largest axis length** for both target and each object.  
3. Calculates a **uniform scale factor** based on this ratio.  
4. Applies the new scale.  
5. Optionally recenters the object to match the target’s bounding box center.

**Automatic Skipping:**  
Objects with zero dimension (flat geometry or empty scale) are skipped to avoid invalid scaling.

---

## Handlers

### Selection Tracker
Automatically updates the **target assignment** based on selection events.

- If only one object is selected, it becomes the new default target.  
- If the stored target is deleted or missing, it clears the reference.

---

## Example Workflow

1. Select your **reference object** (the desired scale).  
2. Run **“Set Target from Active”** to mark it as the scale target.  
3. Select other objects you wish to resize.  
4. Run **“Rescale to Target”** — all selected objects now match the target’s bounding box scale.  
5. Optionally enable **“Center objects to target after scaling”** to align them.

---

## Notes

- Rescaler uses **world-space bounding boxes**, making it compatible with rotated or transformed objects.  
- Works on all object types that provide valid bounding box data (Meshes, Curves, Texts, etc.).  
- Fully undoable — every operation integrates into Blender’s Undo stack.  
- Automatically updates when objects are added or removed.
