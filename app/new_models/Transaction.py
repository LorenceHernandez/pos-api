
from enum import Enum
from itertools import groupby
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, computed_field
from app.new_models.Discount import CustomerDiscountType, TransactionDiscount
from app.new_models.Labtest import Labtest
from app.new_models.Package import Package, PackageType
from app.utils.utils import getLocalDateStr, getLocalTimeStr


class TransactionPackage(Package):
    discount: TransactionDiscount = None

class TenderType(str, Enum):
    CASH = "CASH"
    CHEQUE = "CHEQUE"

class TransactionItem(Labtest):
    package: TransactionPackage = None

    # @computed_field
    # @property
    # def packageId(self) -> str:
    #     return self.package.id


    
class CreateTransaction(BaseModel):
    branchId: str
    customerId: str
    cashierId: str
    referredById: str = None
    requestedById: str = None
    date: str = Field(default_factory=getLocalDateStr)
    transactionDate: str = Field(default_factory=getLocalTimeStr)
    transactionNo: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transactionItems: List[TransactionItem] = Field(min_length=1)
    discounts: List[TransactionDiscount] = None
    tenderType: TenderType
    tenderAmount: float
    invoiceNumber: int = None

class Transaction(CreateTransaction):
    # branchId: str
    # customerId: str
    # referredById: str = None
    # requestedById: str = None
    # date: str = Field(default_factory=getLocalDateStr)
    # transactionDate: str = Field(default_factory=getLocalTimeStr)
    # transactionNo: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # transactionItems: List[TransactionItem] = Field(min_length=1)
    # discounts: List[TransactionDiscount] = None
    # tenderType: TenderType
    # tenderAmount: float

    @computed_field
    @property
    def totalGrossSales(self) -> float:
        return self.sum(self.getItemPrices(self.transactionItems))

    @computed_field
    @property
    def totalNetSales(self) -> float:
        totalSales = self.computeTotalSales()
        totalDiscount = self.computeTotalMemberDiscount(totalSales)
        totalNetSales = totalSales - totalDiscount
        return totalNetSales    

    @computed_field
    @property
    def totalDiscount(self) -> float:
        return self.totalGrossSales - self.totalNetSales

    @computed_field
    @property
    def totalMemberDiscount(self) -> float:
        totalSales = self.computeTotalSales()
        totalDiscount = self.computeTotalMemberDiscount(totalSales)
        return totalDiscount

    @computed_field
    @property
    def change(self) -> float:
        return self.tenderAmount - self.totalNetSales
    
    def computeTotalMemberDiscount(self, totalSales) -> float:
        discounts = self.filterDiscounts(lambda i: i.customerDiscountType == CustomerDiscountType.GOVERNMENT_BENEFICIARY)
        totalDiscount = self.sumTotalDiscount(discounts, totalSales)
        return totalDiscount

    def computeTotalSales(self) -> float:
        packageSales = self.computeTotalPackageSales()
        promoSales = self.computeTotalPromoSales()
        totalSales = packageSales + promoSales
        return totalSales

    def computeTotalPackageSales(self) -> float:
        items = self.filterItemsByNotType(PackageType.PROMO)
        totalPrice =  self.sum(self.getItemPrices(items))

        discounts = self.filterDiscounts(lambda i: i.packageType != PackageType.PROMO and i.customerDiscountType != CustomerDiscountType.GOVERNMENT_BENEFICIARY)
        totalDiscount = self.sumTotalDiscount(discounts, totalPrice)
        return totalPrice - totalDiscount
    
    def computeTotalPromoSales(self) -> float:
        totalPromoPrice: float = 0.0

        items = self.filterItems(lambda i: i.package.type == PackageType.PROMO)
        items = groupby(items, lambda i: i.package.id)

        for _, groupItems in items:
            groupItems = list(groupItems)
            discount = groupItems[0].package.discount

            prices = self.getItemPrices(groupItems)
            totalPrice = self.sum(prices)
            totalPrice -= discount.calculateTotalDiscount(totalPrice)

            totalPromoPrice += totalPrice
            
        return totalPromoPrice
   
    def filterItems(self, func) -> List[TransactionItem]:
        return list(filter(func, self.transactionItems))

    def filterItemsByNotType(self, type: PackageType) -> List[TransactionItem]:
        #Filter all items that exactly unmatch with type even if item package is none
        return self.filterItems(lambda i: i.package.type != type)
    
    def filterItemsByPackage(self, packageId: str, type: PackageType) -> List[TransactionItem]:
        #Short circuit - filter all items that package is not none and match with id and type
        return self.filterItems(lambda i: i.package != None and (i.package.id == packageId and i.package.type == type))

    def filterDiscounts(self, func) -> List[TransactionDiscount]:
        if(self.discounts == None):
            return []
        return list(filter(func, self.discounts))
    
    def getItemPrices(self, items: List[TransactionItem]):
        return list(map(lambda i: i.price, items))
    
    def getDiscountValues(self, discounts: List[TransactionDiscount], sales: float):
        values: List[float] = []
        for discount in discounts:
            values.append(discount.calculateTotalDiscount(sales))
        return values
    
    def sumTotalDiscount(self, discounts: List[TransactionDiscount], sales: float):
        discounts = self.getDiscountValues(discounts, sales)
        return self.sum(discounts)
    
    def sum(self, items):
        sum: float = 0
        for item in items:
            sum += item
        return sum
    